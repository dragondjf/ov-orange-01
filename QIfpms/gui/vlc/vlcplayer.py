#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys
import vlc
import os
import time


class File:

    def __init__(self, path, media):
        self.path = path
        self.media = media


class Main(QWidget):

    def __init__(self):
        super(QWidget, self).__init__()

        self.setStyleSheet('''
        QWidget {
          background-color: #000;
          color: #FFF;
        }
        QLabel {
          font-size: 18px;
        }
        ''')

        self.screen = QWidget()
        self.screen.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.vlc = vlc.Instance()
        self.player = self.vlc.media_player_new()
        self.player.set_hwnd(self.screen.winId())

        self.mainBox = QVBoxLayout()
        self.setLayout(self.mainBox)
        self.mainBox.addWidget(self.screen)

        self.label = QLabel()
        self.label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.mainBox.addWidget(self.label)
        self.label.hide()

        self.slider = Slider(Qt.Horizontal, self)
        self.slider.player = self.player
        self.slider.setMaximum(65536)
        self.slider.sliderMoved.connect(self.setPosition)
        self.mainBox.addWidget(self.slider)
        self.slider.hide()

        self.timer = QTimer(self)
        self.timer.setInterval(200)
        self.timer.timeout.connect(self.update)

        self.files = []
        for arg in sys.argv[1:]:
            media = self.vlc.media_new(arg)
            self.files.append(File(arg, media))

        self.index = 0
        self.play()

    def play(self):
        self.player.set_media(self.files[self.index].media)
        self.player.play()
        m = self.player.get_media()
        self.label.setText(' '.join([
            '%d / %d' % (self.index + 1, len(self.files)),
            self.files[self.index].path,
        ]))
        self.timer.start()
        print(self.player.video_get_title_description())
        print(self.player.get_title())
        print(self.player.has_vout())
        self.player.set_fullscreen(True)

    def playOrPause(self):
        self.player.pause()
        self.timer.start()

    def setPosition(self, position):
        self.player.set_position(position / 65536)

    def update(self):
        self.slider.setValue(self.player.get_position() * 65536)
        if not self.player.is_playing():
            self.timer.stop()

    def mspf(self):
        return int(1000 // (self.player.get_fps() or 25))

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Q:
            sys.exit(0)
        elif event.key() == Qt.Key_D:
            self.player.set_time(self.player.get_time() + 3000)
        elif event.key() == Qt.Key_A:
            self.player.set_time(self.player.get_time() - 3000)
        elif event.key() == Qt.Key_S:
            self.player.set_time(self.player.get_time() + 10000)
        elif event.key() == Qt.Key_W:
            self.player.set_time(self.player.get_time() - 10000)
        elif event.key() == Qt.Key_C:
            self.player.set_time(self.player.get_time() + self.mspf())
        elif event.key() == Qt.Key_X:
            self.player.set_time(self.player.get_time() - self.mspf())
        elif event.key() == Qt.Key_Space:
            self.playOrPause()
        elif event.key() == Qt.Key_F:
            filename = os.path.join(os.path.expanduser("~"), os.path.basename(
                self.files[self.index].path) + "-" + str(time.time()) + ".png")
            self.player.video_take_snapshot(0, filename, 0, 0)
        elif event.key() == Qt.Key_J:
            self.index += 1
            if self.index == len(self.files):
                self.index = 0
            self.play()
        elif event.key() == Qt.Key_K:
            self.index -= 1
            if self.index < 0:
                self.index = len(self.files) - 1
            self.play()
        elif event.key() == Qt.Key_E:
            if self.label.isHidden():
                self.label.show()
                self.slider.show()
            else:
                self.label.hide()
                self.slider.hide()
        elif event.key() == Qt.Key_1:
            self.player.set_rate(1)
        elif event.key() == Qt.Key_2:
            self.player.set_rate(1.2)
        elif event.key() == Qt.Key_3:
            self.player.set_rate(1.5)
        elif event.key() == Qt.Key_4:
            self.player.set_rate(2)
        elif event.key() == Qt.Key_5:
            self.player.set_rate(3)


class Slider(QSlider):

    def __init__(self, *args):
        super(QSlider, self).__init__(*args)
        self.player = None

    def mousePressEvent(self, event):
        self.setValue(self.maximum() * event.x() / self.width())
        self.player.set_position(self.value() / self.maximum())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    m = Main()
    m.show()
    sys.exit(app.exec_())
    # import vlc
    # p=vlc.MediaPlayer('test.mp4')
    # p.play()
