try:
    from PySide2 import QtCore,QtWidgets
except ImportError:
    from PyQt5 import QtCore,QtWidgets
import sys
from gui_main import MainWindow,dpiCheck
import os
import platform


def go():
    if platform.system() == "Darwin":
        os.environ['QT_MAC_WANTS_LAYER'] = '1'
        
    app = QtWidgets.QApplication(sys.argv)
    dpiCheck()
    dialog = MainWindow()
    dialog.show()
    app.exec_()


if __name__ == "__main__":
    go()
