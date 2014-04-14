#!/usr/bin/python
# -*- coding: utf-8 -*-

from PyQt5 import QtWidgets
from gui import MainWindow, GuiManger
from app import StatusClientThread
from gui.uiconfig import windowsoptions
from gui.dialogs import weblogin

from gui import signal_DB
import threading
import websocket
import json


# def on_open(ws):
#     print ("on_open")

# def on_message(ws, message):
#      ws.guimanger.statusManager(json.loads(message))

# def on_error(ws, error):
#      print (error)

# def on_close(ws):
#      print ("on_close")

# def webSocketServer(guimanger):
#     websocket.WebSocketApp.guimanger = guimanger
#     ws = websocket.WebSocketApp("ws://localhost:8888/pushstatus", on_open=on_open, on_message=on_message, on_error=on_error, on_close=on_close)
#     ws.run_forever()

if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)

    loginsettings = windowsoptions['weblogin_window']
    login_flag, results = weblogin(loginsettings)
    if login_flag:
        mainwindow = MainWindow()
        guimanger = GuiManger(results)
        StatusClientThread(results[0]).start()
        mainwindow.show()
        sys.exit(app.exec_())

        # mainwindow = MainWindow()
        # guimanger = GuiManger()
        # mainwindow.show()
        # t = threading.Thread(target=webSocketServer, args=(guimanger,))
        # t.daemon = True  # thread dies when main thread (only non-daemon thread) exits.
        # t.start()
        # sys.exit(app.exec_())
