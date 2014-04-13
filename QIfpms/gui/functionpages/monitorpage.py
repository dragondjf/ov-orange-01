#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from gui.mainwindow.guimanger import collectView, views
from gui.uiconfig import windowsoptions
# from gui.mainwindow.guimanger import signal_DB


class Splitter(QtWidgets.QSplitter):

    def __init__(self, parent=None):
        super(Splitter, self).__init__(parent)

        self.paListPanel = QtWidgets.QFrame()
        self.paListPanel.setFixedWidth(views['MainWindow'].width() * 0.22)

        self.mapPanel = MapPanel(self)

        self.addWidget(self.paListPanel)
        self.addWidget(self.mapPanel)

        self.setCollapsible(0, False)


class MonitorPage(QtWidgets.QFrame):

    viewID = "MonitorPage"

    @collectView
    def __init__(self, parent=None):
        super(MonitorPage, self).__init__(parent)
        self.parent = parent
        self.initData()
        self.initUI()

    def initData(self):
        pass

    def initUI(self):
        splitter = Splitter()
        mainlayout = QtWidgets.QVBoxLayout()
        mainlayout.addWidget(splitter)
        mainlayout.setContentsMargins(0, 0, 0, 0)
        mainlayout.setSpacing(0)
        self.setLayout(mainlayout)


class MapPanel(QtWidgets.QFrame):

    viewID = "MapPanel"

    @collectView
    def __init__(self, parent=None):
        super(MapPanel, self).__init__(parent)
        self.parent = parent
        self.initData()
        self.createPAContextMenu()
        self.initUI()

    def initData(self):
        pass

    def initUI(self):
        self.scene = DiagramScene(self.paContextMenu, self)
        self.view = MapGraphicsView(self)
        self.view.setScene(self.scene)

        mainlayout = QtWidgets.QVBoxLayout()
        mainlayout.addWidget(self.view)
        mainlayout.setContentsMargins(0, 0, 0, 0)
        mainlayout.setSpacing(0)
        self.setLayout(mainlayout)

    def contextMenuEvent(self, event):

        self.changeBackgroundAction = QtWidgets.QAction(self.tr("修改防区地图"), self, triggered=self.view.actionChangeBackground)
        self.getPAsAction = QtWidgets.QAction(self.tr("获取所有防区"), self, triggered=self.actionGetPAs)
        self.clearPAsAction = QtWidgets.QAction(self.tr("清除所有防区"), self, triggered=self.actionClearPAs)

        menu = QtWidgets.QMenu(self)
        menu.addAction(self.changeBackgroundAction)
        menu.addAction(self.getPAsAction)
        menu.addAction(self.clearPAsAction)
        menu.exec_(event.globalPos())

    def createPAContextMenu(self):
        self.disabledAction = QtWidgets.QAction("禁用", self, triggered=self.actionDiabled)
        self.attributeAction = QtWidgets.QAction("属性", self, triggered=self.actionAttribute)
        self.paContextMenu = QtWidgets.QMenu(self)
        self.paContextMenu.addAction(self.disabledAction)
        self.paContextMenu.addAction(self.attributeAction)

    def actionDiabled(self):
        pass

    def actionAttribute(self):
        pass

    def actionClearPAs(self):
        self.scene.clear()

    def actionGetPAs(self):
        # pas = []

        # for i in range(20):
        #    pa = {
        #         "x": i * 30,
        #         "y": i * 30,
        #         'name': "PA1"
        #    }
        #    pas.append(pa)

        # self.scene.createItems(pas)
        pass


class PAItem(QtWidgets.QGraphicsPixmapItem):

    def __init__(self, contextMenu, parent=None):
        super(PAItem, self).__init__(parent)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)
        self.setTransformationMode(QtCore.Qt.SmoothTransformation)
        self.contextMenu = contextMenu
        self.initData()
        self.setPixmap(self.greenPixmap)

    def initData(self):
        self.redPixmap = QtGui.QPixmap("gui/skin/images/colorball3/red.png").scaled(64, 64)
        self.greenPixmap = QtGui.QPixmap("gui/skin/images/colorball3/green.png").scaled(64, 64)
        self.yellowPixmap = QtGui.QPixmap("gui/skin/images/colorball3/yellow.png").scaled(64, 64)
        self.grayPixmap = QtGui.QPixmap("gui/skin/images/colorball3/gray.png").scaled(64, 64)

        self.pixmaps = [
            self.grayPixmap, self.grayPixmap, 
            self.greenPixmap, self.greenPixmap, 
            self.redPixmap, self.yellowPixmap, self.redPixmap
        ]

    def contextMenuEvent(self, event):
        self.scene().clearSelection()
        self.setSelected(True)
        self.contextMenu.exec_(event.screenPos())


class DiagramScene(QtWidgets.QGraphicsScene):

    itemInserted = QtCore.pyqtSignal(PAItem)

    itemSelected = QtCore.pyqtSignal(PAItem)

    viewID = "DiagramScene"

    @collectView
    def __init__(self, itemMenu, parent=None):
        super(DiagramScene, self).__init__(parent)
        self.itemMenu = itemMenu

    def mouseDoubleClickEvent(self, event):
        if (event.button() != QtCore.Qt.LeftButton):
            return
        item = PAItem(self.itemMenu)
        self.addItem(item)
        item.setPos(event.scenePos())
        self.itemInserted.emit(item)
        super(DiagramScene, self).mouseDoubleClickEvent(event)

    def mouseMoveEvent(self, event):
        for item in self.selectedItems():
            if item.pos().x() < 5:
                item.setX(5)
            elif item.pos().y() < 5:
                item.setY(5)
            elif item.pos().x() > self.width() - 69:
                item.setX(self.width() - 69)
            elif item.pos().y() > self.height() - 69:
                item.setY(self.height() - 69)
            else:
                super(DiagramScene, self).mouseMoveEvent(event)


class MapGraphicsView(QtWidgets.QGraphicsView):

    viewID = "MapGraphicsView"

    @collectView
    def __init__(self, parent=None):
        """
        QGraphicsView that will show an image scaled to the current widget size
        using events
        """
        self.parent = parent
        super(MapGraphicsView, self).__init__(parent)
        self.setDragMode(self.RubberBandDrag)
        self.setRenderHint(QtGui.QPainter.Antialiasing)
        self.setRubberBandSelectionMode(QtCore.Qt.ContainsItemShape)
        self.setViewportUpdateMode(QtWidgets.QGraphicsView.BoundingRectViewportUpdate)
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setResizeAnchor(self.AnchorUnderMouse)
        self.setCacheMode(QtWidgets.QGraphicsView.CacheBackground)

    def actionChangeBackground(self, firstFalg=False):
        if "viewbgfile" in windowsoptions:
            if firstFalg:
                bgfile = windowsoptions["viewbgfile"]
            else:
                bgfile = self.setOpenFileName()
        else:
            if firstFalg:
                return
            bgfile = self.setOpenFileName()

        if bgfile:
            windowsoptions["viewbgfile"] = bgfile
            self.initScene(bgfile)

    def initScene(self, bgfile):
        if views['MainWindow'].isFullScreen():
            self.viewWidth = self.parent.size().width()-5
            self.viewHeight = self.parent.size().height()-5
            windowsoptions["viewWidth"] = self.viewWidth
            windowsoptions["viewHeight"] = self.viewHeight
        else:
            if 'viewWidth' in windowsoptions:
                self.viewWidth = windowsoptions["viewWidth"]
                self.viewHeight = windowsoptions["viewHeight"]
            else:
                return

        self.scene().setSceneRect(QtCore.QRectF(0, 0, self.viewWidth, self.viewHeight))
        bgPixmap = QtGui.QPixmap(bgfile).scaled(self.viewWidth, self.viewHeight)
        bgBrush = QtGui.QBrush(bgPixmap)
        self.scene().setBackgroundBrush(bgBrush)

    def setOpenFileName(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self,
                "QFileDialog.getOpenFileName()",
                self.tr("All(*); Images (*.png *.xpm *.jpg)"),options=options)
        if fileName:
            return fileName

    def resizeEvent(self, event):
        self.actionChangeBackground(True)
        super(MapGraphicsView, self).resizeEvent(event)
