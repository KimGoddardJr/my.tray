#! /usr/local/bin python3

try:
    from PySide2 import QtCore, QtGui
    from PySide2.QtGui import QIcon
    from PySide2.QtWidgets import *
except:
    from PyQt5 import QtCore, QtGui
    from PyQt5.QtGui import QIcon
    from PyQt5.QtWidgets import *
import os
import sys
import getpass
import json

from img_utils import *
from tray_menu import *
from draw_items import juche, bergli
import settings as anus_settings


def main():
    work_user = ["hslu", "admin"]
    app = QApplication(sys.argv)

    if getpass.getuser() in work_user:
        m_ico = bergli()
    else:
        m_ico = juche()

    cur_path = os.path.dirname(os.path.realpath(__file__))
    software_files = os.path.join(cur_path, "..", "..", "launcher.files")

    tray = QSystemTrayIcon()
    tray.setIcon(m_ico)
    tray.setVisible(True)

    menu = PatxiMenu(software_files)
    menu.BuildMenu()
    # menu.addAction(sys.exit(app.exec_()))
    # menu.action_dict["BLENDER BUILD"][0].triggered.connect(lambda: print(menu.action_dict["BLENDER BUILD"][1]))

    tray.setContextMenu(menu)
    
    # menu.show()
    tray.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

