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
import re
from functools import partial
import configparser
from glob import glob
import subprocess
import platform

from actions import *
from states import CheckOCIOState
from img_utils import *
from draw_items import *
from triggerers import trigger_app


class AnusMenu(QMenu):
    def __init__(self, software_files: str, launchers: str, parent=None):
        super(AnusMenu, self).__init__(parent)
        home = os.path.expanduser("~")
        self.project = None
        # temporary PATH for launchers. Needds to be made userdefinable
        self.launchers = launchers
        self.software_files = software_files
        self.applications = {}
        self.icons = {}
        self.DictOfParse()
        self.action_dict = {}

    def BuildMenu(self):

        self.CurProject()

        self.addSeparator()

        for category, apps in sorted(self.applications.items()):
            cat_menu = QMenu(category.upper(),self)
            cat_menu.setIcon(iconFromBase64(self.icons[category].encode()))

            for name, app in sorted(apps.items()):
                print(name)
                soft_ico = iconFromBase64(app["icon"].encode())
                action = QAction(soft_ico, name, self)

                exec_cmds = []
                init_launcher = os.path.join(self.launchers, app["launcher"])
                if platform.system() == "Windows":
                    init_launcher += ".ps1"
                    exec_cmds.append("powershell.exe")
                    exec_cmds.append(init_launcher)
                else:
                    init_launcher += ".sh"
                    exec_cmds.append(init_launcher)

                param = f"{app['param1']}"
                exec_cmds.append(param)

                action.triggered.connect(
                    partial(self.RunLauncher, exec_cmds)
                )
                cat_menu.addAction(action)
                self.action_dict[name] = (action, app["launcher"])
                # cat_menu.addAction(soft_ico, name).triggered.connect(lambda: self.RunLauncher(app["launcher"]))
            self.addMenu(cat_menu)

        self.AdditionalActions()

    def RebuildMenu(self, text):
        print(text)
        # remove everything from menu but last widget
        self.clear()
        self.BuildMenu()
        self.PROJECT.setText(self.get_current_project())

    def Parser(self):
        glob_pattern = os.path.join(self.software_files, "*")
        software_files = sorted(glob(glob_pattern))
        parser = configparser.ConfigParser()
        parser.read(software_files)

        return parser

    def DictOfParse(self):
        parser = self.Parser()
        for section_name in parser.sections():
            category = parser.get(section_name, "family")
            family = parser.get(section_name, "family")

            if not self.applications.get(category):
                self.applications[category] = {}

            if not self.icons.get(category):
                self.icons[category] = ""

            if not self.applications[category].get(section_name):
                self.applications[category][section_name] = {}

            for name, value in parser.items(section_name):
                self.applications[category][section_name][name] = value
                if name == "categoryicon" or (
                    name == "icon" and self.icons[category] == ""
                ):
                    self.icons[category] = value

    def TriggerLauncher(self, app_name):
        action, launcher = self.action_dict[app_name]
        action.triggered.connect(lambda: self.RunLauncher(launcher))

    def RunLauncher(self, exec_cmds):
        subprocess.Popen(exec_cmds)

    def CurProject(self):
        self.PROJECT = QAction(self)
        if self.project:
            self.PROJECT.setText(self.project)
        else:
            self.PROJECT.setText(self.get_current_project())
            self.PROJECT.setFont(QtGui.QFont("Comic Sans MS", 10, QtGui.QFont.Bold))

        self.addAction(self.PROJECT)
        cmds = []

        if platform.system() == "Windows":
            cmds.append("powershell.exe")
        cmds.append(os.getenv("ANUS_PM_LAUNCHER"))

        self.PROJECT.triggered.connect(lambda: self.RunLauncher(cmds))

    def AdditionalActions(self):

        self.addSeparator()

        OCIO = QAction(checkable=True)
        state_ico, ocio_state = CheckOCIOState(OCIO)
        OCIO.setIcon(state_ico)
        OCIO.setText(ocio_state)
        OCIO.triggered.connect(lambda: ToggleIconAction(OCIO))

        self.addAction(OCIO)

        std_refresh_pixmap = getattr(QStyle, "SP_BrowserReload")
        std_exit_pixmap = getattr(QStyle,"SP_DialogCloseButton")
        refresh_ico = QWidget().style().standardIcon(std_refresh_pixmap)
        exit_ico = QWidget().style().standardIcon(std_exit_pixmap)
        REFRESH = QAction(refresh_ico, "Refresh", self)
        REFRESH.triggered.connect(lambda: self.RebuildMenu("REBUILDING"))

        LEAVE = QAction(exit_ico,"Exit",self)
        LEAVE.triggered.connect(sys.exit)

        self.addAction(REFRESH)
        self.addAction(LEAVE)
    
    def get_current_project(self):
        project_path = os.getenv("ANUS_PROJECT_MEMORY")
        if os.path.exists(project_path):
            cur_proj_line = open(project_path).read()
            base = os.path.basename(cur_proj_line)
            cur_proj = base.split(".")[0]
        else:
            cur_proj = "No Project Set"
        
        return cur_proj

