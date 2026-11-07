#requires -Version 5.1
[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

Write-Host ''
Write-Host '  CYBBIG - installation locale' -ForegroundColor Cyan
Write-Host '  -----------------------------' -ForegroundColor DarkCyan

$npm = Get-Command npm.cmd -ErrorAction SilentlyContinue
if (-not $npm) { throw "npm.cmd est introuvable. Installez Node.js 22 ou plus récent." }
if (-not (Get-Command node -ErrorAction SilentlyContinue)) { throw "Node.js est introuvable." }

$python = Join-Path $Root 'backend\.venv\Scripts\python.exe'
if (-not (Test-Path $python)) {
    Write-Host '[1/6] Création de l environnement Python...' -ForegroundColor Yellow
    $py = Get-Command py -ErrorAction SilentlyContinue
    if ($py) {
        & py -3.11 -m venv (Join-Path $Root 'backend\.venv')
    } else {
        & python -m venv (Join-Path $Root 'backend\.venv')
    }
    if (-not (Test-Path $python)) {
        $python = Join-Path $Root 'backend\.venv\Scripts\python.exe'
        if (-not (Test-Path $python)) { throw "La création du venv Python a échoué." }
    }
} else {
    Write-Host '[1/6] Environnement Python déjà présent.' -ForegroundColor Green
}

Write-Host '[2/6] Installation des dépendances Python...' -ForegroundColor Yellow
& $python -m pip install --upgrade pip --quiet
& $python -m pip install -r (Join-Path $Root 'backend\requirements.txt')
if ($LASTEXITCODE -ne 0) { throw "L installation des dépendances Python a échoué." }

Write-Host '[3/6] Installation des dépendances de l interface...' -ForegroundColor Yellow
Push-Location (Join-Path $Root 'frontend')
try { & $npm install; if ($LASTEXITCODE -ne 0) { throw 'npm install (frontend) a échoué.' } }
finally { Pop-Location }

Write-Host '[4/6] Installation d Electron...' -ForegroundColor Yellow
& $npm install
if ($LASTEXITCODE -ne 0) { throw 'npm install (racine) a échoué.' }

if (-not (Test-Path (Join-Path $Root 'node_modules\electron\dist\electron.exe'))) {
    Write-Host 'Téléchargement du binaire Electron...' -ForegroundColor Yellow
    Push-Location $Root
    try { & node .\node_modules\electron\install.js; if ($LASTEXITCODE -ne 0) { throw 'Le téléchargement d Electron a échoué.' } }
    finally { Pop-Location }
}

Write-Host '[5/6] Compilation de l interface...' -ForegroundColor Yellow
& $npm run build
if ($LASTEXITCODE -ne 0) { throw 'La compilation du frontend a échoué.' }

Write-Host '[6/6] Initialisation de la base locale...' -ForegroundColor Yellow
Push-Location (Join-Path $Root 'backend')
try {
    & $python -c "from app import db; db.init_db(); print('Base SQLite initialisée.')"
    if ($LASTEXITCODE -ne 0) { throw 'L initialisation de la base a échoué.' }
}
finally { Pop-Location }

Write-Host ''
Write-Host '  Installation terminée.' -ForegroundColor Green
Write-Host '  Démarrez avec : scripts\start.ps1' -ForegroundColor Cyan
Write-Host ''
