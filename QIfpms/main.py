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


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)

    loginsettings = windowsoptions['weblogin_window']
    login_flag, address = weblogin(loginsettings)
    if login_flag:
        mainwindow = MainWindow()
        guimanger = GuiManger(address)
        statusThread = StatusClientThread(address)
        statusThread.daemon = True
        statusThread.start()
        mainwindow.show()
        sys.exit(app.exec_())
