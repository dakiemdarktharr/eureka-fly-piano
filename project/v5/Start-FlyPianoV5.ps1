$ErrorActionPreference = 'Stop'
$taskApp = Join-Path $PSScriptRoot 'dist/FlyPianoLabV5/FlyPianoLabV5.exe'
if (Test-Path -LiteralPath $taskApp) {
    Start-Process -FilePath $taskApp -WorkingDirectory $PSScriptRoot -WindowStyle Hidden
} else {
    $taskPython = Join-Path $PSScriptRoot '../v4/.venv/Scripts/python.exe'
    if (-not (Test-Path -LiteralPath $taskPython)) { throw 'Missing v4 Python environment; see README_vi.md.' }
    Start-Process -FilePath $taskPython -ArgumentList ('"' + (Join-Path $PSScriptRoot 'app.py') + '"') -WorkingDirectory $PSScriptRoot -WindowStyle Hidden
}
