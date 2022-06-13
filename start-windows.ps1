$env:DEVEL_BASE = "$HOME\devel"

conda activate vfxpipeline

# Powershell.exe  -windowstyle hidden -executionpolicy remotesigned -File  "$env:DEVEL_BASE\launchers\windows\anus_tray.ps1"

Powershell.exe -File  "$env:DEVEL_BASE\launchers\windows\anus_tray.ps1"

