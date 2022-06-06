#!/usr/bin/env bash

# eval "$(conda shell.bash hook)"
ECOBIN=${HOME}/.${USER}_ecobin
source $HOME/anaconda3/bin/activate vfxpipeline
export ECO_ENV=${ECOBIN}/ecosystem-env/
export TOOLS="base,tractor2.4,anus1.0.0"

# export XDG_SESSION_TYPE=wayland
# export QT_QPA_PLATFORM=wayland
# export QT_QPA_PLATFORM=xcb

SCRIPT_PATH=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

python "${SCRIPT_PATH}/anus_tray/main.py"