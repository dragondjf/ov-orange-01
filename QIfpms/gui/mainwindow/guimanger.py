#!/usr/bin/python
# -*- coding: utf-8 -*-

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets
import functools
import random
from datetime import datetime

views = {}


def collectView(fuc):

    @functools.wraps(fuc)
    def wrapper(*args, **kwargs):
        self = args[0]
        views.update({self.viewID: self})
        fuc(*args, **kwargs)
    return wrapper


class SignalDB(QtCore.QObject):

    pas_sin = QtCore.pyqtSignal(list)
    alarm_sin = QtCore.pyqtSignal(list)
    simpleAlarm_sin = QtCore.pyqtSignal(dict)

    def __init__(self):
        super(SignalDB, self).__init__()

signal_DB = SignalDB()


status_name = ['disable', 'disconn', 'connect', 'alarm_minor', 'alarm_critical', 'alarm_fiber_break', 'alarm_blast']
status_name_zh = ['禁用','断开', '运行', '预警', '告警', '断纤', '爆破']
status_color = ['gray','gray', 'green', 'lightgreen', 'red', 'yellow', 'red']


class GuiManger(QtCore.QObject):

    """docstring for GuiManger"""

    def __init__(self, parent=None):
        super(GuiManger, self).__init__()
        self.parent = parent

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.statusChange)
        #self.timer.start(1000)
        self.initData()
        self.initSignalConnect()
        self.initPAs()

    def initData(self):
        self.count = 0
        self.paitems = {}

    def initSignalConnect(self):
        signal_DB.pas_sin.connect(self.createItems)
        signal_DB.alarm_sin.connect(self.addItem)
        signal_DB.simpleAlarm_sin.connect(self.updatePAStatus)

    def initPAs(self):
        pas = []
        for i in range(1, 11):
            did = i / 2 + 1
            pid = i % 2
            pa = {
                'status': i,
                'enable': True,
                'status_change_time': datetime.today().strftime("%Y-%m-%d %H:%M:%S"),
                'name': '防区1-1',
                'did': did,
                'pid': pid,
                'cx': 50 * i,
                'cy': 100 * (pid + 1),
                'sid': 'PA-%d-%d' % (did, pid),
                'dec': ''
            }
            pas.append(pa)

        signal_DB.pas_sin.emit(pas)

    def statusChange(self):
        i = random.randint(1, 10)
        did = i / 2 + 1
        pid = i % 2
        pa = {
            'status': random.randint(0, 6),
            'status_change_time': datetime.today().strftime("%Y-%m-%d %H:%M:%S"),
            'enable': True,
            'name': '防区1-1',
            'did': did,
            'pid': pid,
            'cx': 60 * did,
            'cy': 300 * pid,
            'sid': 'PA-%d-%d' % (did, pid),
            'dec': ''
        }
        self.count += 1
        alarm = [self.count, pa['status'], pa['did'], pa['pid'], pa['status_change_time'], "", "yes"]
        signal_DB.alarm_sin.emit(alarm)

        simpleAlarm = {'sid': pa['sid'], 'status': pa['status']}

        signal_DB.simpleAlarm_sin.emit(simpleAlarm)

    @QtCore.pyqtSlot(list)
    def createItems(self, pas):
        from gui.functionpages import PAItem
        for pa in pas:
            item = PAItem(views['DiagramScene'].itemMenu)
            item.setPos(QtCore.QPointF(pa['cx'], pa['cy']))
            views['DiagramScene'].addItem(item)
            self.paitems.update({pa['sid']: item})

    @QtCore.pyqtSlot(dict)
    def updatePAStatus(self, alarm):
        sid = alarm['sid']
        status = alarm['status']
        item = self.paitems[sid]
        item.setPixmap(item.pixmaps[status])

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
