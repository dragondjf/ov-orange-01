#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from .qrc_icons import *
from .guiconfig import collectView, views


class TitleBar(QtWidgets.QFrame):

    viewID = "TitleBar"

    @collectView
    def __init__(self, parent=None):
        super(TitleBar, self).__init__(parent)

        self.setObjectName("TitleBar")
        self.initData()
        self.initUI()

    def initData(self):
        self.minIcon = QtGui.QIcon(":/icons/dark/appbar.minus.png")
        self.maxIcon = QtGui.QIcon(":/icons/dark/appbar.fullscreen.box.png")
        self.normalIcon = QtGui.QIcon(":/icons/dark/appbar.app.png")
        self.closeIcon = QtGui.QIcon(":/icons/dark/appbar.close.png")

    def initUI(self):
        baseHeight = 20
        self.setFixedHeight(baseHeight)

        iconBaseSize = QtCore.QSize(20, baseHeight)
        self.minButton = QtWidgets.QToolButton()
        self.minButton.setIcon(self.minIcon)
        self.minButton.setIconSize(iconBaseSize)

        self.maxButton = QtWidgets.QToolButton()
        self.maxButton.setIconSize(iconBaseSize)
        self.initfullScreen()

        self.closeButton = QtWidgets.QToolButton()
        self.closeButton.setIconSize(iconBaseSize)
        self.closeButton.setIcon(QtGui.QIcon(":/icons/dark/appbar.close.png"))

        mainLayout = QtWidgets.QHBoxLayout()
        mainLayout.addStretch()
        mainLayout.addWidget(self.minButton)
        mainLayout.addWidget(self.maxButton)
        mainLayout.addWidget(self.closeButton)
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.setSpacing(0)
        self.setLayout(mainLayout)

        self.minButton.clicked.connect(self.actionMin)
        self.maxButton.clicked.connect(self.actionMax)
        self.closeButton.clicked.connect(self.actionClose)

    def initfullScreen(self):
        mainwindow = views['MainWindow']
        if mainwindow.fullscreenflag:
            mainwindow.showFullScreen()
            self.maxButton.setIcon(self.maxIcon)
        else:
            mainwindow.showNormal()
            self.maxButton.setIcon(self.normalIcon)

    def actionMin(self):
        mainwindow = views['MainWindow']
        mainwindow.showMinimized()

    def actionMax(self):
        mainwindow = views['MainWindow']
        if mainwindow.isFullScreen():
            mainwindow.showNormal()
            self.maxButton.setIcon(self.maxIcon)
        else:
            mainwindow.showFullScreen()
            self.maxButton.setIcon(self.normalIcon)

    def actionClose(self):
        mainwindow = views['MainWindow']
        mainwindow.close()

    def mouseDoubleClickEvent(self, event):
        self.actionMax()
