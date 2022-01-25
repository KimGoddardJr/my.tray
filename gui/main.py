#! /usr/local/bin python3

from PySide2 import QtCore, QtGui
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import *
import os
import sys

from tray_menu import *
from img_utils import *
from draw_items import *


def main():
    app = QApplication(sys.argv)

    m_ico_b64 = iconFromBase64(menu_image)
    m_ico = QIcon(m_ico_b64)

    cur_path = os.path.dirname(os.path.realpath(__file__))
    software_files = f"{cur_path}/../../launcher.files"

    tray = QSystemTrayIcon()
    tray.setIcon(m_ico_b64)
    tray.setVisible(True)

    menu = PatxiMenu(software_files)
    menu.BuildMenu()

    menu.addAction("Quit").triggered.connect(sys.exit)

    tray.setContextMenu(menu)

    # menu.show()
    tray.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

