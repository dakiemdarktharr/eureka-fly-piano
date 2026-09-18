$ErrorActionPreference = 'Stop'
$v4Root = $PSScriptRoot
$v4Exe = Join-Path $v4Root 'dist/FlyPianoLabV4/FlyPianoLabV4.exe'
if (Test-Path -LiteralPath $v4Exe) {
  Start-Process -FilePath $v4Exe -WorkingDirectory (Split-Path $v4Exe) -WindowStyle Hidden
} else {
  $v4Python = Join-Path $v4Root '.venv/Scripts/python.exe'
  if (-not (Test-Path -LiteralPath $v4Python)) { throw 'Install requirements.txt in project/v4/.venv first.' }
  Start-Process -FilePath $v4Python -ArgumentList @('app.py') -WorkingDirectory $v4Root -WindowStyle Hidden
}
