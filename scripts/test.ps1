#requires -Version 5.1
[CmdletBinding()]
param([switch]$SkipSmoke)

$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$Backend = Join-Path $Root 'backend'
$Python = Join-Path $Backend '.venv\Scripts\python.exe'
if (-not (Test-Path $Python)) { throw "Environnement Python absent. Exécutez scripts\setup.ps1." }

Write-Host ''
Write-Host '  CYBBIG - tests' -ForegroundColor Cyan
Write-Host '  --------------'

Write-Host '[1/2] Tests unitaires et API...' -ForegroundColor Yellow
Push-Location $Backend
try {
    & $Python -m pytest -q tests
    if ($LASTEXITCODE -ne 0) { throw 'Les tests pytest ont échoué.' }
}
finally { Pop-Location }

if ($SkipSmoke) {
    Write-Host 'Tests terminés (smoke ignoré).' -ForegroundColor Green
    exit 0
}

Write-Host '[2/2] Parcours de bout en bout...' -ForegroundColor Yellow
$proc = $null
$existing = $false
try {
    $null = Invoke-RestMethod -Uri 'http://127.0.0.1:8765/api/health' -TimeoutSec 2
    $existing = $true
    Write-Host 'Un backend est déjà actif : réutilisation.' -ForegroundColor DarkGray
} catch { }

if (-not $existing) {
    $proc = Start-Process -FilePath $Python `
        -ArgumentList @('-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', '8765', '--log-level', 'warning') `
        -WorkingDirectory $Backend -PassThru -WindowStyle Hidden

    $ready = $false
    for ($i = 0; $i -lt 60; $i++) {
        Start-Sleep -Milliseconds 500
        try {
            $health = Invoke-RestMethod -Uri 'http://127.0.0.1:8765/api/health' -TimeoutSec 2
            if ($health.status -eq 'ok') { $ready = $true; break }
        } catch { }
        if ($proc.HasExited) { break }
    }
    if (-not $ready) { throw "Le backend de test n a pas démarré. Consultez backend\data\backend.log." }
}

try {
    Push-Location $Backend
    try {
        & $Python smoke.py
        if ($LASTEXITCODE -ne 0) { throw 'Le parcours smoke a échoué.' }
    }
    finally { Pop-Location }
}
finally {
    if ($proc -and -not $proc.HasExited) {
        & taskkill /pid $proc.Id /T /F | Out-Null
    }
}

Write-Host 'Tous les tests sont passés.' -ForegroundColor Green
