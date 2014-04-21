#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import json


mainwindow = {
    'title': "QIFPMS",
    'size': (0.8, 0.9),
    'minsize': (0.4, 0.3),
    'icon': "gui/skin/images/QIfpms.png",
    'fullscreenflag': True,
}


__softwarename__ = 'QIFPMS'
__author__ = ""
__url__ = ""
__description__ = '''
    This is a SoftwareFrame based on PyQt5.
'''
__logoico__ = "gui/skin/images/QIfpms.png"
__version__ = '1.0.0'


logo_ico = __logoico__
logo_img_url = "gui/skin/images/ov-orange-green.png"
logo_title = u''

from .dialogconfig import dialogsettings

try:
    with open(os.sep.join([os.getcwd(), 'options', 'windowsoptions.json']), 'r') as f:
        windowsoptions = json.load(f)
        # logger.info('Load windowsoptions from file')
except:
    # logger.exception(e)
    # logger.info('Load windowsoptions from local')
    windowsoptions = {
        'mainwindow': mainwindow,
        'splashimg': os.sep.join([os.getcwd(), 'skin', 'images', 'splash.png']),
        'viewbgfile':  os.sep.join([os.getcwd(), 'gui', 'skin', 'images', 'compayimage.jpg']),
        'MapMenuflag': True,
        'PAMenuflag': False,
    }
    windowsoptions.update(dialogsettings)
