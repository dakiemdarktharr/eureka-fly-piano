param([switch]$SkipInstall)
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
$TaskVenv = Join-Path $PSScriptRoot '.venv'
$TaskPython = Join-Path $TaskVenv 'Scripts/python.exe'
if (!(Test-Path -LiteralPath $TaskPython)) {
    python -m venv $TaskVenv
    if ($LASTEXITCODE -ne 0) { throw 'Python 3.11+ is required.' }
}
if (!$SkipInstall) {
    & $TaskPython -m pip install -r environment.lock
    if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed.' }
}
& $TaskPython -m pip check
if ($LASTEXITCODE -ne 0) { throw 'Dependency verification failed.' }
if (!(Get-Command ffmpeg -ErrorAction SilentlyContinue)) { throw 'ffmpeg must be on PATH.' }
$env:OPENBLAS_NUM_THREADS = '1'
& $TaskPython reproduce.py core
if ($LASTEXITCODE -ne 0) { throw 'Core reproduction failed; inspect preceding output.' }
