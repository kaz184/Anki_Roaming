# -*- coding: utf-8 -*-
# Copyright: Damien Elmes <anki@ichi2.net>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html

from aqt import mw
from aqt.qt import *

config = mw.addonManager.getConfig(__name__)

FONT      = config.get('font', "Meiryo")
WEB_FONT_SIZE = config.get('web_font_size', 20)
APP_FONT_SIZE = config.get('app_font_size', 20)

def changeGlobalFontSize():
    font = QFont(FONT)
    font.setPixelSize(APP_FONT_SIZE)
    mw.setFont(font)
    QApplication.setFont(font)

def changeWebFontSize():
    ws = QWebEngineSettings.globalSettings()
    ws.setFontSize(QWebEngineSettings.MinimumFontSize, WEB_FONT_SIZE)

def changeFontSize():
    changeGlobalFontSize()
    changeWebFontSize()

changeFontSize()
