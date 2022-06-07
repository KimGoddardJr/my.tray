#!/usr/bin/env bash

# eval "$(conda shell.bash hook)"
#ECOBIN=${HOME}/.${USER}_ecobin
#source $HOME/anaconda3/bin/activate vfxpipeline
#export ECO_ENV=${ECOBIN}/ecosystem-env/
#export TOOLS="base,tractor2.4,anus1.0.0"



#export XDG_SESSION_TYPE=wayland
#export QT_QPA_PLATFORM=wayland
#export QT_QPA_PLATFORM=xcb

SCRIPT_PATH=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

# ECOSYSTEM_ENV


# LAUNCHERS
export LAUNCHER_FILES="${SCRIPT_PATH}/../launcher.files"
export LAUNCHERS="${SCRIPT_PATH}/../launchers/unix"

# APPS
export ANUS_PROJECT_MANAGER=$SCRIPT_PATH/anus_tray/project_manager
export ANUS_PROJECT_MEMORY=$HOME/.anus/project_history.txt

export ANUS_PROJECT_SETUP=$SCRIPT_PATH/../my.project-setup


python "${SCRIPT_PATH}/anus_tray/main.py"