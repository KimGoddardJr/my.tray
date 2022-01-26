#! /usr/local/bin python3

from PySide2 import QtCore, QtGui
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import *
import os
import sys
import getpass
import json

from actions import *
from img_utils import *
from tray_menu import *
from draw_items import juche,bergli
from states import CheckOCIOState


def main():
    work_user = ["hslu","admin"]
    app = QApplication(sys.argv)

    if getpass.getuser() in work_user:
        m_ico = bergli()
    else:
        m_ico = juche()

    cur_path = os.path.dirname(os.path.realpath(__file__))
    software_files = os.path.join(cur_path,"..","..","launcher.files")

    tray = QSystemTrayIcon()
    tray.setIcon(m_ico)
    tray.setVisible(True)

    menu = PatxiMenu(software_files)
    menu.BuildMenu()

    # menu.action_dict["BLENDER BUILD"][0].triggered.connect(lambda: print(menu.action_dict["BLENDER BUILD"][1]))
    

    OCIO = QAction(checkable=True)
    state_ico, ocio_state = CheckOCIOState(OCIO)
    OCIO.setIcon(state_ico)
    OCIO.setText(ocio_state)
    OCIO.triggered.connect(lambda: ToggleIconAction(OCIO))

    menu.addAction(OCIO)

    menu.addAction("Quit").triggered.connect(sys.exit)

    tray.setContextMenu(menu)

    # menu.show()
    tray.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

