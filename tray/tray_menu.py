from PySide2 import QtCore, QtGui
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import *
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


class PatxiMenu(QMenu):
    def __init__(self, software_files: str, parent=None):
        super(PatxiMenu, self).__init__(parent)
        home = os.path.expanduser('~')
        self.launchers = os.path.join(home,"devel","launchers")
        self.software_files = software_files
        self.applications = {}
        self.icons = {}
        self.DictOfParse()
        self.action_dict = {}

    def BuildMenu(self):

        for category, apps in sorted(self.applications.items()):
            cat_menu = QMenu(category.upper())
            cat_menu.setIcon(iconFromBase64(self.icons[category].encode()))

            for name, app in sorted(apps.items()):
                print(name)
                soft_ico = iconFromBase64(app["icon"].encode())
                action = QAction(soft_ico, name, self)
                init_launcher = os.path.join(self.launchers,app["launcher"])
                param = f"{app['param1']}"
                action.triggered.connect(partial(self.RunLauncher,init_launcher,param))
                cat_menu.addAction(action)
                self.action_dict[name] = (action, app["launcher"])
                # cat_menu.addAction(soft_ico, name).triggered.connect(lambda: self.RunLauncher(app["launcher"]))
            self.addMenu(cat_menu)

        self.AdditionalActions()
    
    def RebuildMenu(self):
        self.clear()
        self.BuildMenu()
        
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

    def TriggerLauncher(self,app_name):
        action,launcher = self.action_dict[app_name]
        action.triggered.connect(lambda: self.RunLauncher(launcher))

    def RunLauncher(self, launch_cmd, param):
        print(launch_cmd)
        if platform.system() == "Windows":
            print(launch_cmd)
            print(param)
            subprocess.Popen(["powershell.exe",launch_cmd,param])
        else:
            subprocess.Popen([launch_cmd,param])
    
    def AdditionalActions(self):

        OCIO = QAction(checkable=True)
        state_ico, ocio_state = CheckOCIOState(OCIO)
        OCIO.setIcon(state_ico)
        OCIO.setText(ocio_state)
        OCIO.triggered.connect(lambda: ToggleIconAction(OCIO))

        self.addAction(OCIO)

        std_refresh_pixmap = getattr(QStyle,'SP_BrowserReload')  
        refresh_ico = QWidget().style().standardIcon(std_refresh_pixmap)
        REFRESH = QAction(refresh_ico,"Refresh",self)
        REFRESH.triggered.connect(lambda: self.RebuildMenu())

        self.addAction(REFRESH)
