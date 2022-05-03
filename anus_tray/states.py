try:
    from PySide2.QtWidgets import *
except:
    from PyQt5.QtWidgets import *
import json
import os
import settings as anus_settings
from widgets import *


def settings(cfg_path: str):
    with open(cfg_path) as f:
        return json.load(f)

def CheckOCIOState(action: QAction):
    on,off = Switches()
    OCIO_STATE = settings(anus_settings.SETTINGS)["OCIO"]
    if OCIO_STATE:
        action.setChecked(True)
        return on,"OCIO on"
    else:
        action.setChecked(False)
        return off,"OCIO off"

def ChangeOCIOState(OCIO_STATE: bool):
    settings_dict = settings(anus_settings.SETTINGS)
    if OCIO_STATE:
        settings_dict["OCIO"] = True
    else:
        settings_dict["OCIO"] = False
    with open(anus_settings.SETTINGS, "w") as f:
        json.dump(settings_dict, f)
