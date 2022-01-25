import json
import os
from widgets import *

def settings():
    cur_path = os.path.dirname(os.path.realpath(__file__))
    settings_path = os.path.join(cur_path,"..","settings.json")
    with open(settings_path) as f:
        return json.load(f)

def CheckOCIOState():
    on,off = Switches()
    OCIO_STATE = settings()["OCIO"]
    if OCIO_STATE:
        return on,"OCIO ON"
    else:
        return off,"OCIO OFF"

# def ChangeOCIOState():
