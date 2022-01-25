from PySide2 import QtGui
from PySide2.QtWidgets import *
from widgets import *
from states import *


def ToggleIconAction(action: QAction):
    on_ico, off_ico = Switches()
    if action.isChecked():
        action.setIcon(on_ico)
        action.setText("OCIO ON")
        CheckOCIOState()
    elif not action.isChecked():
        action.setIcon(off_ico)
        action.setText("OCIO OFF")