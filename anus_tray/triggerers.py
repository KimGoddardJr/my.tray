import subprocess
import os
import platform

def trigger_app(app_env):
    app_base = os.getenv(app_env)
    app_main = os.path.join(app_base,"main.py")
    subprocess.Popen(["python", app_main])