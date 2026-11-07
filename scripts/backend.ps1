#requires -Version 5.1
[CmdletBinding()]
param([int]$Port = 8765)

$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $Root 'backend\.venv\Scripts\python.exe'
if (-not (Test-Path $Python)) { throw "Environnement Python absent. Exécutez scripts\setup.ps1." }

$env:CYBBIG_PORT = "$Port"
Write-Host "Backend Cybbig sur http://127.0.0.1:$Port" -ForegroundColor Cyan
Write-Host 'Ctrl+C pour arrêter.' -ForegroundColor DarkGray
Push-Location (Join-Path $Root 'backend')
try {
    & $Python -m uvicorn app.main:app --host 127.0.0.1 --port $Port
}
finally { Pop-Location }
