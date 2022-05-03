#!/usr/bin/env bash

# eval "$(conda shell.bash hook)"

source $HOME/anaconda3/bin/activate vfxpipeline

# export XDG_SESSION_TYPE=wayland
# export QT_QPA_PLATFORM=wayland
# export QT_QPA_PLATFORM=xcb

SCRIPT_PATH=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

python "${SCRIPT_PATH}/anus_tray/main.py"