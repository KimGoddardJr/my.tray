from PySide2 import QtCore, QtGui
from PySide2.QtWidgets import *


def iconFromBase64(base64):
    pixmap = QtGui.QPixmap()
    pixmap.loadFromData(QtCore.QByteArray.fromBase64(base64))
    icon = QtGui.QIcon(pixmap)
    return icon

def ToggleIconAction(action: QAction, icon: QtGui.QIcon):
    action.setIcon(icon)
