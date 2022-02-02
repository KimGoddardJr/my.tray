#!/usr/bin/env bash

# eval "$(conda shell.bash hook)"

source $HOME/anaconda3/bin/activate vfxpipeline

SCRIPT_PATH=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

python3 "${SCRIPT_PATH}/tray/main.py"