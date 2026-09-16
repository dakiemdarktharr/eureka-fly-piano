param([switch]$SkipInstall)
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
& "$PSScriptRoot/reproduce_core.ps1" -SkipInstall:$SkipInstall
$TaskPython = Join-Path $PSScriptRoot '.venv/Scripts/python.exe'
& $TaskPython reproduce.py all
if ($LASTEXITCODE -ne 0) { throw 'Full reproduction failed.' }
