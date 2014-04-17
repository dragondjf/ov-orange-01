#!/usr/bin/python
# -*- coding: utf-8 -*-

from PyQt5 import QtCore
import json
import time
import websocket
import threading
import requests
from dataBase import signal_DB


class StatusClientThread(threading.Thread, QtCore.QObject):
    """docstring for ClientThread"""
    def __init__(self, address):
        super(StatusClientThread, self).__init__()
        self.address = address
        self.count = 0
        self.wsurl = "ws://%s:%s/pushstatus" % address
        self.ws = websocket.WebSocketApp(self.wsurl, on_open=on_open, on_message=on_message, on_error=on_error, on_close=on_close)
        self.ws.address = self.address
        # websocket.enableTrace(True)

    def run(self):
        self.ws.run_forever()            

count = 0

def on_open(ws):
    response = requests.get('http://%s:%s/palist' % ws.address, timeout=3)
    result = response.json()
    pas = result['protection_areas']
    signal_DB.pas_sin.emit(pas)

def on_message(ws, message):
    global count
    alarm = json.loads(message)
    simpleAlarm = {'sid': alarm['sid'], 'status': alarm['status']}
    signal_DB.simpleAlarm_sin.emit(simpleAlarm)
    count += 1
    changetime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(alarm['status_change_time']))
    alarm = [count, alarm['status'], alarm['did'], alarm['pid'], changetime, "", "yes"]
    signal_DB.alarm_sin.emit(alarm)

def on_error(ws, error):
    print (error)

def on_close(ws):
    print ("on_close")
