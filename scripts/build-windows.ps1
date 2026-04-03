$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RootDir = Split-Path -Parent $ScriptDir
Set-Location $RootDir

python -m pip install --upgrade pip
pip install -r requirements-dev.txt

if (Test-Path build-pyinstaller) { Remove-Item build-pyinstaller -Recurse -Force }
if (Test-Path dist-bin) { Remove-Item dist-bin -Recurse -Force }

pyinstaller `
  --noconfirm `
  --clean `
  --onefile `
  --name copyast `
  --paths src `
  --distpath dist-bin `
  --workpath build-pyinstaller `
  src/app/main.py

Write-Host "Build completed: dist-bin/copyast.exe"