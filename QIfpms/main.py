#!/usr/bin/python
# -*- coding: utf-8 -*-

from PyQt5 import QtWidgets
from gui import MainWindow, GuiManger


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    mainwindow = MainWindow()
    guimanger = GuiManger()
    mainwindow.show()
    sys.exit(app.exec_())
