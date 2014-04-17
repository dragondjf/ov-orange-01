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

from .guiconfig import views


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
        self.paitems = {}
        self.paLabels = {}

    def initSignalConnect(self):
        signal_DB.pas_sin.connect(self.createItems)
        signal_DB.alarm_sin.connect(self.addItem)
        signal_DB.simpleAlarm_sin.connect(self.updatePAStatus)

    @QtCore.pyqtSlot(list)
    def createItems(self, pas):
        from gui.functionpages import PAItem
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

    def statusManager(self, alarm):
        '''
        {"did": 1, "status": 2, "pid": 2, "status_change_time": 1397487425, "sid": "PA-1-2"}
        '''
        self.count += 1
        alarmList = [self.count, alarm['status'], alarm['did'], alarm['pid'], alarm['status_change_time'], alarm['sid'], "yes"]
        self.addItem(alarmList)
        simpleAlarm = {'sid': alarm['sid'], 'status': alarm['status']}
        self.updatePAStatus(simpleAlarm)

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
