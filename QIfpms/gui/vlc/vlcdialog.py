#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
import sys
from .vlc import Instance
import os
import time
from gui.uiconfig import logo_ico
from gui.mainwindow.titlebar import DialogTitleBar
from gui.mainwindow.qrc_icons import *


class LoadingWidget(QtWidgets.QLabel):

    style = '''
        QLabel{
            background-color: transparent;
            font-size: 20px;
            font-family: "Verdana";
            border: none;
            color: white;
        }
    '''

    def __init__(self, parent=None):
        super(LoadingWidget, self).__init__(parent)
        self.parent = parent
        self.setFixedSize(100, 100)
        self.setStyleSheet(self.style)
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setAutoFillBackground(True)
        loadinggif = os.sep.join([os.getcwd(), 'gui', 'skin', 'images', 'loading.gif'])
        self.movie = QtGui.QMovie(loadinggif)
        self.movie.setCacheMode(QtGui.QMovie.CacheAll)
        self.setMovie(self.movie)
        self.movie.setSpeed(100)

    def movecenter(self):
        qr = self.frameGeometry()
        pr = self.parent.frameGeometry()
        cp = QtCore.QRect(0, 0, pr.width(), pr.height()).center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

class VLCDialog(QtWidgets.QDialog):
    """docstring for VLCDialog"""
    style = '''
        QPushButton
        {
            color: rgb(255, 255, 255);
            background-color: rgb(167, 205, 255);
            background: green;
            border:none;
            font-family: "Verdana";
            font-size: 15px;
            text-align: center;
            width: 60px;
        }
        QPushButton:hover, QPushButton:pressed , QPushButton:checked
        {
            background-color: rgb(85, 170, 255);
            text-align: center;
            font-family: "Verdana";
        }
        QPushButton:hover
        {
            background-repeat:no-repeat;
            background-position: center left;
        }
        QPushButton:pressed, QPushButton:checked
        {
            background-repeat:no-repeat;
            background-position: center left;
        }

        QPushButton:disabled{
            color: gray;
            background-color: rgb(167, 205, 255);
        }

        QFrame#TitleBar{
            background-color: green;
        }

        QLabel{
            background-color: transparent;
            font-size: 12px;
            font-family: "Verdana";
            border: none;
            color: white;
            padding-left: 5px;
        }

        QToolButton{
            background-color: transparent;
            color: white;
        }

        QToolButton:hover{
            background-color: lightgreen;
            border: 1px;
        }
    '''

    def __init__(self, paname, url):
        super(VLCDialog, self).__init__()
        self.paname = paname
        self.url = url
        self.setWindowTitle(self.paname)
        self.setWindowIcon(QtGui.QIcon(logo_ico))  # 设置程序图标
        self.setMinimumSize(600, 400)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowMinimizeButtonHint)  # 无边框， 带系统菜单， 可以最小化
        self.setSizeGripEnabled(True)
        self.initData()
        self.initUI()
        self.initTimer()

    def initData(self):
        pass

    def initTimer(self):
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.loadvideo)
        self.timer.setSingleShot(5000)
        self.timer.start()

    def loadvideo(self):
        self.initVLC()
        self.media = self.vlc.media_new(self.url)
        self.player.set_media(self.media)
        self.player.play()
        # self.loadingwidget.hide()

    def initUI(self):
        self.titlebar = DialogTitleBar(self.paname, self)
        self.screen = QtWidgets.QFrame()
        self.screen.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        # self.loadingwidget = LoadingWidget(self)

        mainlayout = QtWidgets.QVBoxLayout()
        mainlayout.addWidget(self.titlebar)
        mainlayout.addWidget(self.screen)
        mainlayout.setContentsMargins(0, 0, 0, 0)
        mainlayout.setSpacing(0)
        self.setLayout(mainlayout)
        self.setStyleSheet(self.style)

        # self.loadingwidget.movecenter()
        # self.loadingwidget.movie.setSpeed(100)
        # self.loadingwidget.movie.start()

    def initVLC(self):
        self.vlc = Instance()
        self.player = self.vlc.media_player_new()
        self.player.set_hwnd(self.screen.winId())

    def mousePressEvent(self, event):
        # 鼠标点击事件
        if event.button() == QtCore.Qt.LeftButton:
            self.dragPosition = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseReleaseEvent(self, event):
        # 鼠标释放事件
        if hasattr(self, "dragPosition"):
            del self.dragPosition

    def mouseMoveEvent(self, event):
        # 鼠标移动事件
        if hasattr(self, "dragPosition"):
            if event.buttons() == QtCore.Qt.LeftButton:
                self.move(event.globalPos() - self.dragPosition)
                event.accept()

    def closeEvent(self, event):
        self.player.stop()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    m = VLCDialog("PA-1-1", 'http://42.96.155.222:9999/static/pm.mp4')
    m.show()
    sys.exit(app.exec_())
    # import vlc
    # p=vlc.MediaPlayer('test.mp4')
    # p.play()
