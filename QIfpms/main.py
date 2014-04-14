#!/usr/bin/python
# -*- coding: utf-8 -*-

from PyQt5 import QtWidgets
from gui import MainWindow, GuiManger
from app import StatusClientThread
from gui.uiconfig import windowsoptions
from gui.dialogs import weblogin

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
