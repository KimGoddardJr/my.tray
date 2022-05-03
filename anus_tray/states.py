try:
    from PySide2.QtWidgets import *
except:
    from PyQt5.QtWidgets import *
import json
import os
from widgets import *

def settings_path():
    cur_path = os.path.dirname(os.path.realpath(__file__))
    cfg_path = os.path.join(cur_path,"..","settings.json")
    return cfg_path


def settings(cfg_path: str):
    with open(cfg_path) as f:
        return json.load(f)

def CheckOCIOState(action: QAction):
    on,off = Switches()
    OCIO_STATE = settings(settings_path())["OCIO"]
    if OCIO_STATE:
        action.setChecked(True)
        return on,"OCIO on"
    else:
        action.setChecked(False)
        return off,"OCIO off"

def ChangeOCIOState(OCIO_STATE: bool):
    settings_dict = settings(settings_path())
    if OCIO_STATE:
        settings_dict["OCIO"] = True
    else:
        settings_dict["OCIO"] = False
    with open(settings_path(), "w") as f:
        json.dump(settings_dict, f)
