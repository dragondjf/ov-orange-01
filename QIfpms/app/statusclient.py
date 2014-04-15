#!/usr/bin/python
# -*- coding: utf-8 -*-

from PyQt5 import QtCore
import json
import time
import websocket
import threading
import requests
from dataBase import signal_DB


class StatusClientThread(threading.Thread):
    """docstring for ClientThread"""
    def __init__(self, address):
        super(StatusClientThread, self).__init__()
        self.address = address
        self.count = 0
        self.wsurl = "ws://%s:%s/pushstatus" % address
        self.ws = websocket.WebSocketApp(self.wsurl, on_open=self.on_open, on_message=self.on_message, on_error=self.on_error, on_close=self.on_close)
        self.ws.address = self.address
        websocket.enableTrace(True)

    def run(self):
        self.ws.run_forever()            

    @staticmethod
    def on_open(ws):
        response = requests.get('http://%s:%s/palist' % ws.address, timeout=3)
        result = response.json()
        pas = result['protection_areas']
        signal_DB.pas_sin.emit(pas)

    @staticmethod
    def on_message(ws, message):
        alarm = json.loads(message)
        simpleAlarm = {'sid': alarm['sid'], 'status': alarm['status']}
        signal_DB.simpleAlarm_sin.emit(simpleAlarm)
        self.count += 1
        changetime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(alarm['status_change_time']))
        alarm = [self.count, alarm['status'], alarm['did'], alarm['pid'], changetime, "", "yes"]
        signal_DB.alarm_sin.emit(alarm)

    @staticmethod
    def on_error(ws, error):
        print (error)

    @staticmethod
    def on_close(ws):
        print ("on_close")

        