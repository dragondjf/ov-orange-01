#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from gui.mainwindow import collectView, views
from gui.uiconfig import windowsoptions


class Splitter(QtWidgets.QSplitter):

    def __init__(self, parent=None):
        super(Splitter, self).__init__(parent)

        if 'pawidth' not in windowsoptions:
            windowsoptions['pawidth'] = views['MainWindow'].width() * 0.22

        self.paListPanel = PATable(self)
        self.paListPanel.setFixedWidth(windowsoptions['pawidth'])

        self.mapPanel = MapPanel(self)

        self.addWidget(self.paListPanel)
        self.addWidget(self.mapPanel)


class PATable(QtWidgets.QTableWidget):

    viewID = "PATable"

    @collectView
    def __init__(self, parent=None):
        super(PATable, self).__init__(parent)
        self.parent = parent
        self.setShowGrid(False)
        self.setSelectionBehavior(self.SelectRows)
        self.setSelectionMode(self.SingleSelection)
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.setEditTriggers(self.NoEditTriggers)

        self.initHeader()
        self.initColumnWidth()

    def initHeader(self):
        self.setColumnCount(3)
        # headerview = QtWidgets.QHeaderView(QtCore.Qt.Horizontal, self)
        self.horizontalHeader().hide()
        self.verticalHeader().hide()
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

    def initColumnWidth(self):
        self.setColumnWidth(0, 60)
        self.setColumnWidth(2, 60)
        self.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Fixed)
        self.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.Fixed)

    def changeColor(self, row, bgcolor):
        for col in range(self.columnCount()):
            item = self.item(row, col)
            bgBrush = QtGui.QBrush(QtGui.QColor(bgcolor))
            item.setBackground(bgBrush)

    def addItem(self, row, message, bgcolor="gray", fgcolor="white"):
        print(row, message)
        self.insertRow(row)
        
        bgBrush = QtGui.QBrush(QtGui.QColor(bgcolor))
        fgBrush = QtGui.QBrush(QtGui.QColor(fgcolor))

        for col in range(self.columnCount()):
            if col == 0:
                item = QtWidgets.QTableWidgetItem("")
            elif col == 1:
                item = QtWidgets.QTableWidgetItem(message)
            elif col == 2:
                item = QtWidgets.QTableWidgetItem("设置")
            item.setBackground(bgBrush)
            item.setForeground(fgBrush)
            self.setItem(row, col, item)

# class PAPanel(QtWidgets.QScrollArea):

#     viewID = "PAPanel"

#     @collectView
#     def __init__(self, parent=None):
#         super(PAPanel, self).__init__(parent)
#         self.parent = parent
#         self.initData()
#         self.initUI()

#     def initData(self):
#         pass

#     def initUI(self):
#         self.paFrame = QtWidgets.QWidget()
#         self.paFrame.resize(QtCore.QSize(windowsoptions['pawidth'] - 40, windowsoptions['viewHeight']))
#         self.paFrame.setObjectName("PAFrame")
#         mainlayout = QtWidgets.QVBoxLayout()
#         mainlayout.setSpacing(2)
#         # for i in range(100):
#         #     mainlayout.addWidget(PALabel("%d"%i, self))
#         self.paFrame.setLayout(mainlayout)
#         self.setWidget(self.paFrame)


# class PALabel(QtWidgets.QPushButton):

#     def __init__(self, name, parent=None):
#         super(PALabel, self).__init__(parent)
#         self.parent = parent
#         self.setFlat(True)
#         # self.setDisabled(True)
#         self.setObjectName("PALabel")
#         self.setFixedSize(windowsoptions['pawidth'] - 40, 35)
#         self.setText(name)
#         self.settingButton = QtWidgets.QPushButton("设置", self)
#         self.settingButton.setObjectName("PAsetting")
#         self.settingButton.setFixedSize(40, 35)
#         self.settingButton.hide()
#         self.settingButton.move(self.width() - 40, 0)
#         self.installEventFilter(self)

#     def eventFilter(self, obj, event):
#         if event.type() == QtCore.QEvent.HoverMove:
#             self.settingButton.show()
#             return True
#         elif event.type() == QtCore.QEvent.Leave:
#             self.settingButton.hide()
#             return True
#         else:
#             return super(PALabel, self).eventFilter(obj, event)

#     def changeColor(self, bgcolor):
#         style = "QPushButton#PALabel{background-color: %s;} " % bgcolor
#         style_setting = '''QPushButton#PAsetting{
#             color: white;
#             background-color: green;
#         }'''
#         self.setStyleSheet(style)
#         self.settingButton.setStyleSheet(style_setting)


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
        self.setPixmap(self.grayPixmap)

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
