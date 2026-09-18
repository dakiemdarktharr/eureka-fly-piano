$ErrorActionPreference = 'Stop'
$taskExe = Join-Path $PSScriptRoot 'dist\FlyPianoLab\FlyPianoLab.exe'
if (Test-Path -LiteralPath $taskExe) { Start-Process -FilePath $taskExe -WindowStyle Hidden; exit }
$taskPython = Join-Path $PSScriptRoot '..\v2\.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $taskPython)) { throw 'Run setup from README_v3.md or use the standalone Windows bundle.' }
$taskApp = Join-Path $PSScriptRoot 'app.py'
Start-Process -FilePath $taskPython -ArgumentList @('"' + $taskApp + '"') -WorkingDirectory $PSScriptRoot -WindowStyle Hidden
