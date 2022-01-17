import sys

from PySide2.QtWidgets import (
    QApplication,
    QMenu,
    QPushButton,
    QSystemTrayIcon,
    QWidgetAction,
)

app = QApplication(sys.argv)
menu = QMenu()
button = QPushButton("yoba")
action = QWidgetAction(menu)
action.setDefaultWidget(button)
menu.addAction(action)
menu.addAction("Quit").triggered.connect(sys.exit)
tray = QSystemTrayIcon()
tray.setContextMenu(menu)
menu.show()
sys.exit(app.exec_())
