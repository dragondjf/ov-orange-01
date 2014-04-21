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
from gui.vlc import VLCDialog


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
        self.alarmhistory = []

    def initSignalConnect(self):
        signal_DB.pas_sin.connect(self.createItems)
        signal_DB.alarm_sin.connect(self.addItem)
        signal_DB.simpleAlarm_sin.connect(self.updatePAStatus)
        signal_DB.settingsIndex_sin.connect(self.settings)
        signal_DB.videoIndex_sin.connect(self.vedioplay)

        views['DiagramScene'].selectionChanged.connect(self.selectPALabel)
        views['PATable'].itemSelectionChanged.connect(self.selectPAItem)

    def selectPALabel(self):
        try:
            paSelectItems = views['DiagramScene'].selectedItems()
            for key, value in self.paitems.items():
                if value in paSelectItems:
                    index = self.paLabels[key]
                    views['PATable'].selectRow(index)
        except:
            pass

    def selectPAItem(self):
        index = views['PATable'].selectedRanges()[0].topRow()
        sid = self.pas[index]['sid']
        views['DiagramScene'].clearSelection()
        self.paitems[sid].setSelected(True)

    @QtCore.pyqtSlot(list)
    def createItems(self, pas):
        from gui.functionpages import PAItem, PATextItem
        self.pas = pas
        i = 0
        for pa in pas:
            item = PAItem(views['DiagramScene'].itemMenu)
            item.setPos(QtCore.QPointF(pa['cx']*2, pa['cy']*1.2))
            textItem = PATextItem(pa['name'], item)
            textItem.setPos(-5, 45)
            item.setZValue(len(pas) - i)
            views['DiagramScene'].addItem(item)
            self.paitems.update({pa['sid']: item})

            status = status_name_zh[pa['status']]
            name = pa['sid'] + '  ' + pa['name']

            views['PATable'].addItem(i, [status, name])
            self.paLabels.update({pa['sid']: i})
            i += 1
            self.updatePAStatus({'sid': pa['sid'], 'status': pa['status']})

    @QtCore.pyqtSlot(dict)
    def updatePAStatus(self, alarm):
        sid = alarm['sid']
        status = alarm['status']
        item = self.paitems[sid]
        item.setPixmap(item.pixmaps[status])  # 改变地图上防区的状态

        row = self.paLabels[sid]
        views['PATable'].changeColor(row, status_color[status])  # 改变整行的颜色
        views['PATable'].item(row, 1).setText(status_name_zh[status]) # 改变当前行第二列的状态

    def vedioplay(self, index):
        pa = self.pas[index]
        if 'url' not in pa:
            pa['url'] = 'http://42.96.155.222:9999/static/pm.mp4'
        vlcdialog = VLCDialog(pa['name'], pa['url'])
        vlcdialog.show()

    @QtCore.pyqtSlot(int)
    def settings(self, index):
        flag, formdata = settingsinput(self.pas[index], windowsoptions['settingsdialog'])
        if flag:
            payload = {
                "did": self.pas[index]['did'],
                "pid": self.pas[index]['pid'],
                "enable": int(formdata['enable'])
            }
            response = requests.post('http://%s:%s/setprotect' % ("localhost", "8888"), params=payload, timeout=3)
            if int(response.json()) == 1:
                if int(formdata['enable']) == 1:
                    views['StatusBar'].showMessage(self.pas[index]['name'] + "   启用成功")
                elif int(formdata['enable']) == 0:
                    views['StatusBar'].showMessage(self.pas[index]['name'] + "   禁用成功")
            else:
                if int(formdata['enable']) == 1:
                    views['StatusBar'].showMessage("发送启用%s 命令失败" % self.pas[index]['name'])
                elif int(formdata['enable']) == 0:
                    views['StatusBar'].showMessage("发送禁用%s 命令失败" % self.pas[index]['name'])

    @QtCore.pyqtSlot(list)
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

        self.alarmhistory.append(alarm)

    def getPAList(self):
        response = requests.get('http://%s:%s/palist' % self.address, timeout=3)
        result = response.json()
        pas = result['protection_areas']
        return pas
