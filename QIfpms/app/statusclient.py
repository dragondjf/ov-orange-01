#!/usr/bin/python
# -*- coding: utf-8 -*-

from PyQt5 import QtCore
import json
import time
import websocket
import threading
from dataBase import signal_DB


class StatusClientThread(threading.Thread, QtCore.QObject):
    """docstring for ClientThread"""
    def __init__(self, address):
        super(StatusClientThread, self).__init__()
        self.address = address
        self.count = 0
        self.wsurl = "ws://%s:%s/pushstatus" % address

    def run(self):
        alarm_ws = websocket.create_connection(self.wsurl)
        while True:
            alarm = json.loads(alarm_ws.recv())
            simpleAlarm = {'sid': alarm['sid'], 'status': alarm['status']}
            signal_DB.simpleAlarm_sin.emit(simpleAlarm)
            self.count += 1
            changetime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(alarm['status_change_time']))
            alarm = [self.count, alarm['status'], alarm['did'], alarm['pid'], changetime, "", "yes"]
            signal_DB.alarm_sin.emit(alarm)
