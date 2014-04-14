#!/usr/bin/python
# -*- coding: utf-8 -*-

from PyQt5 import QtCore


class SignalDB(QtCore.QObject):

    loginsin = QtCore.pyqtSignal(dict)
    pas_sin = QtCore.pyqtSignal(list)
    alarm_sin = QtCore.pyqtSignal(list)
    simpleAlarm_sin = QtCore.pyqtSignal(dict)

    def __init__(self):
        super(SignalDB, self).__init__()

signal_DB = SignalDB()
