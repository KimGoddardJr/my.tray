$BASE = "D:\01_projects\2016_DigitalHumans\IA_Space_Pipeline"

conda activate vfxpipeline

$env:ENV_LAUNCHERS="${BASE}\my.launchers"

python "${BASE}\my.tray\tray\main.py" 

