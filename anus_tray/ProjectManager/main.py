from PySide2 import QtCore,QtWidgets
import sys
from gui_main import MainWindow,dpiCheck


def go():
    app = QtWidgets.QApplication(sys.argv)
    dpiCheck()
    dialog = MainWindow()
    dialog.show()
    app.exec_()


if __name__ == "__main__":
    go()
