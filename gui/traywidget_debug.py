from PySide2.QtGui import QIcon
from PySide2.QtWidgets import *


def quit_action_clicked():
    app.quit()


def test_action_clicked():
    pass


app = QApplication([])
app.setQuitOnLastWindowClosed(False)
icon = QIcon("pics/bergli_circle.png")

tray = QSystemTrayIcon()
tray.setIcon(icon)
tray.setVisible(True)

menu = QMenu()

"""
add_action = QAction("Barfoobaz")
menu.addAction(add_action)

test_action = QAction("Foobarbaz")
test_action.triggered.connect(test_action_clicked)
menu.addAction(test_action)
menu.addSeparator()
"""

widget = QWidget()


layout = QVBoxLayout()
innerLayout = QGridLayout()

innerLayout.setSpacing(2)
# innerLayout.setContentsMargins(1, 1, 1, 3)
innerLayout.addWidget(QLabel("Name:"), 0, 0)
innerLayout.addWidget(QLabel("tank"), 0, 1)
innerLayout.addWidget(QLabel("GUID:"), 1, 0)
innerLayout.addWidget(QLabel("12345678901234567890"), 1, 1)
innerLayout.addWidget(QLabel("Status:"), 2, 0)
innerLayout.addWidget(QLabel("healthy"), 2, 1)
innerLayout.addWidget(QPushButton("Touch Me!"), 3, 0)
innerLayout.addWidget(QLineEdit("Write on Me"), 3, 1)
innerLayout.addWidget(QLabel("OCIO"), 4, 0)
innerLayout.addWidget(QCheckBox(), 4, 1)

layout.addLayout(innerLayout)

bar = QProgressBar()
bar.setValue(70)

layout.addWidget(bar)
layout.addWidget(QLabel("Size: 2TB, 1.87TB free"))
layout.setContentsMargins(21, 0, 15, 0)
layout.setSpacing(0)

widget.setLayout(layout)

berAction = QWidgetAction(menu)
berAction.setDefaultWidget(widget)

menu.addAction(berAction)
menu.addSeparator()


action = QAction("Quit")
action.triggered.connect(quit_action_clicked)

menu.addAction(action)

tray.setContextMenu(menu)

app.setStyleSheet(open("style/hslu_animation.css").read())

app.exec_()
