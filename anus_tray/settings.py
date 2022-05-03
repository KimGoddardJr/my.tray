import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")

CONFIG = os.path.join(DATA,"config.json")
SETTINGS = os.path.join(DATA,"settings.json")

POOL = os.path.dirname(BASE)
LAUNCHER_FILES = os.path.join(POOL, "launcher.files")
LAUNCHERS = os.path.join(POOL, "my.launchers")
LAUNCHERS_WIN = os.path.join(LAUNCHERS, "win")
LAUNCHERS_UNIX = os.path.join(LAUNCHERS, "unix")

