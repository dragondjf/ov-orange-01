#!/usr/bin/python
# -*- coding: utf-8 -*-

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets

import random
from datetime import datetime
import json
import threading
import time
from dataBase import signal_DB
import requests
from gui.dialogs import settingsinput
from .guiconfig import views
from gui.uiconfig import windowsoptions


status_name = ['disable', 'disconn', 'connect', 'alarm_minor', 'alarm_critical', 'alarm_fiber_break', 'alarm_blast']
status_name_zh = ['禁用', '断开', '运行', '预警', '告警', '断纤', '爆破']
status_color = ['gray', 'gray', 'green', 'lightgreen', 'red', 'yellow', 'red']


class GuiManger(QtCore.QObject):

    """docstring for GuiManger"""

    def __init__(self, address, parent=None):
        super(GuiManger, self).__init__()
        self.parent = parent
        self.address = address
        self.initData()
        self.initSignalConnect()

    def initData(self):
        self.pas = []
        self.paitems = {}
        self.paLabels = {}

    def initSignalConnect(self):
        signal_DB.pas_sin.connect(self.createItems)
        signal_DB.alarm_sin.connect(self.addItem)
        signal_DB.simpleAlarm_sin.connect(self.updatePAStatus)
        signal_DB.settingsIndex_sin.connect(self.settings)

        views['DiagramScene'].selectionChanged.connect(self.selectPA)

    def selectPA(self):
        paSelectItems = views['DiagramScene'].selectedItems()
        for key, value in self.paitems.items():
            if value in paSelectItems:
                index = self.paLabels[key]
                views['PATable'].selectRow(index)

    @QtCore.pyqtSlot(list)
    def createItems(self, pas):
        from gui.functionpages import PAItem
        self.pas = pas
        i = 0
        for pa in pas:
            item = PAItem(views['DiagramScene'].itemMenu)
            item.setPos(QtCore.QPointF(pa['cx'], pa['cy']))
            views['DiagramScene'].addItem(item)
            self.paitems.update({pa['sid']: item})

            t = pa['sid'] +  '  ' + pa['name']
            views['PATable'].addItem(i, t)
            self.paLabels.update({pa['sid']: i})
            i += 1


    @QtCore.pyqtSlot(dict)
    def updatePAStatus(self, alarm):
        sid = alarm['sid']
        status = alarm['status']
        item = self.paitems[sid]
        item.setPixmap(item.pixmaps[status])

        row = self.paLabels[sid]
        views['PATable'].changeColor(row, status_color[status])

    @QtCore.pyqtSlot(int)
    def settings(self, index):
        flag , formdata = settingsinput(windowsoptions['settingsdialog'])
        if flag:
            payload = {
                "did": self.pas[index]['did'], 
                "pid": self.pas[index]['pid'], 
                "enable": formdata['enable']
            }
            response = requests.post('http://%s:%s/setprotect' % ("localhost", "8888"), params=payload, timeout=3)
            print(response.text)

    def addItem(self, alarm):
        bgcolor = status_color[alarm[1]]
        bgBrush = QtGui.QBrush(QtGui.QColor(bgcolor))
        if bgcolor == "yellow":
            fgBrush = QtGui.QBrush(QtGui.QColor('black'))
        else:
            fgBrush = QtGui.QBrush(QtGui.QColor('white'))
        views['AlarmTable'].insertRow(0)
        for col in range(views['AlarmTable'].columnCount()):
            if col == 1:
                newItem = QtWidgets.QTableWidgetItem(status_name_zh[alarm[col]])
            else:
                newItem = QtWidgets.QTableWidgetItem(str(alarm[col]))
            newItem.setTextAlignment(QtCore.Qt.AlignCenter)
            newItem.setBackground(bgBrush)
            newItem.setForeground(fgBrush)
            views['AlarmTable'] .setItem(0, col, newItem)
