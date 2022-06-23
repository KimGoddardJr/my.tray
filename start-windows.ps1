$env:DEVEL_BASE = "$PSScriptRoot\.."

conda activate vfxpipeline

# Powershell.exe  -windowstyle hidden -executionpolicy remotesigned -File  "$env:DEVEL_BASE\launchers\windows\anus_tray.ps1"

Powershell.exe -File  "$env:DEVEL_BASE\my.launchers\windows\anus_tray.ps1"

