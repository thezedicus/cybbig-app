#requires -Version 5.1
<#
  Construit les installateurs Windows de Cybbig.

  1. Prépare une copie autonome de l'application (release\stage\app) : interface compilée, sources
     modifiables depuis l'éditeur de code, backend et Python embarqué officiel (python.org, signé PSF).
  2. -Package : paquet autonome release\Cybbig-Setup-<version>.zip (« Installer Cybbig.cmd »),
     compatible Smart App Control (aucun exécutable recompilé).
  3. -SetupExe : installateur classique release\setup\Cybbig-Setup-<version>.exe (NSIS via electron-builder).
     Non signé : Smart App Control peut le bloquer.
#>
[CmdletBinding()]
param(
    [switch]$Package,
    [switch]$SetupExe,
    [switch]$StageOnly
)

$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$Release = Join-Path $Root 'release'
$Stage = Join-Path $Release 'stage\app'
$Cache = Join-Path $Release 'cache'
$Version = (Get-Content (Join-Path $Root 'package.json') -Raw | ConvertFrom-Json).version
$PyVersion = '3.11.9'   # même version mineure que l'environnement de développement (modules compilés compatibles)
$PyZip = "python-$PyVersion-embed-amd64.zip"

function Step($text) { Write-Host "  > $text" -ForegroundColor Cyan }
function Mirror($from, $to, [string[]]$extra = @()) {
    $options = @($from, $to, '/MIR', '/NFL', '/NDL', '/NJH', '/NJS', '/NP', '/R:2', '/W:1', '/XD', '__pycache__', '.pytest_cache') + $extra
    & robocopy @options | Out-Null
    if ($LASTEXITCODE -ge 8) { throw "Copie impossible : $from -> $to (robocopy $LASTEXITCODE)" }
}

if (-not ($Package -or $SetupExe -or $StageOnly)) { $Package = $true; $SetupExe = $true }

Write-Host ''
Write-Host "  CYBBIG $Version - construction des installateurs" -ForegroundColor Cyan
Write-Host '  ---------------------------------------------'

Step 'Compilation de l interface'
Push-Location $Root
try {
    $npmCommand = Get-Command npm.cmd -ErrorAction SilentlyContinue
    if ($npmCommand) {
        & $npmCommand.Source run build | Out-Null
    } else {
        # Certains environnements fournissent Node et les dépendances du projet sans npm.
        $nodeCommand = Get-Command node.exe -ErrorAction Stop
        $viteCli = Join-Path $Root 'frontend\node_modules\vite\bin\vite.js'
        if (-not (Test-Path $viteCli)) { throw 'npm.cmd et la CLI Vite locale sont introuvables.' }
        Push-Location (Join-Path $Root 'frontend')
        try { & $nodeCommand.Source $viteCli build } finally { Pop-Location }
    }
    if ($LASTEXITCODE -ne 0) { throw 'La compilation du frontend a échoué.' }
} finally { Pop-Location }

Step 'Copie de l application'
New-Item -ItemType Directory -Force $Stage, $Cache | Out-Null
Mirror (Join-Path $Root 'desktop') (Join-Path $Stage 'desktop')
Mirror (Join-Path $Root 'backend\app') (Join-Path $Stage 'backend\app')
Mirror (Join-Path $Root 'backend\samples') (Join-Path $Stage 'backend\samples')
Copy-Item (Join-Path $Root 'backend\requirements.txt') (Join-Path $Stage 'backend') -Force
# Interface : version compilée + sources (modifiables et recompilables depuis Administration → Code).
Mirror (Join-Path $Root 'frontend\dist') (Join-Path $Stage 'frontend\dist')
Mirror (Join-Path $Root 'frontend\src') (Join-Path $Stage 'frontend\src')
foreach ($f in 'index.html', 'package.json', 'package-lock.json', 'tsconfig.json', 'tsconfig.node.json', 'vite.config.ts') {
    $src = Join-Path $Root "frontend\$f"
    if (Test-Path $src) { Copy-Item $src (Join-Path $Stage 'frontend') -Force }
}
New-Item -ItemType Directory -Force (Join-Path $Stage 'scripts') | Out-Null
Copy-Item (Join-Path $Root 'scripts\install-ollama.ps1') (Join-Path $Stage 'scripts') -Force
# UTF-8 sans BOM : Set-Content -Encoding UTF8 en ajoute un, que electron-builder refuse.
$manifest = [ordered]@{ name = 'cybbig'; productName = 'Cybbig'; version = $Version; description = 'Poste local de cybersécurité défensive'; author = 'Cybbig'; main = 'desktop/main.js'; private = $true } | ConvertTo-Json
[IO.File]::WriteAllText((Join-Path $Stage 'package.json'), $manifest, [Text.UTF8Encoding]::new($false))

Step "Python embarqué $PyVersion"
$zip = Join-Path $Cache $PyZip
if (-not (Test-Path $zip)) {
    Invoke-WebRequest "https://www.python.org/ftp/python/$PyVersion/$PyZip" -OutFile $zip -UseBasicParsing
}
$pyDir = Join-Path $Stage 'backend\python'
if (Test-Path $pyDir) { Remove-Item $pyDir -Recurse -Force }
Expand-Archive $zip -DestinationPath $pyDir -Force
$signature = Get-AuthenticodeSignature (Join-Path $pyDir 'python.exe')
if ($signature.Status -ne 'Valid' -or $signature.SignerCertificate.Subject -notmatch 'Python Software Foundation') {
    Remove-Item $zip -Force
    throw "Signature de python.exe invalide ($($signature.Status)) : archive supprimée, relancez la construction."
}
# Active site-packages dans le Python embarqué.
$pth = Get-ChildItem $pyDir -Filter 'python*._pth' | Select-Object -First 1
(Get-Content $pth.FullName) -replace '^#\s*import site', 'import site' | Set-Content $pth.FullName -Encoding ASCII
Add-Content $pth.FullName 'Lib\site-packages' -Encoding ASCII
# Dépendances : celles, déjà validées sur ce poste, de l'environnement de développement (sans les outils de test).
$sitePackages = Join-Path $Root 'backend\.venv\Lib\site-packages'
Mirror $sitePackages (Join-Path $pyDir 'Lib\site-packages') @('/XD', 'pip', 'setuptools', '_pytest', 'pytest', 'pyflakes', 'pluggy', 'iniconfig', '/XF', 'distutils-precedence.pth')
& (Join-Path $pyDir 'python.exe') -c "import fastapi, uvicorn, requests, bs4, sqlite3; print('python embarque OK')"
if ($LASTEXITCODE -ne 0) { throw 'Le Python embarqué ne charge pas les dépendances.' }

if ($StageOnly) { Write-Host "  Copie prête : $Stage" -ForegroundColor Green; exit 0 }

if ($Package) {
    Step 'Paquet autonome'
    $name = "Cybbig-Setup-$Version"
    $pkg = Join-Path $Release $name
    if (Test-Path $pkg) { Remove-Item $pkg -Recurse -Force }
    Mirror $Stage (Join-Path $pkg 'app')
    Mirror (Join-Path $Root 'node_modules\electron\dist') (Join-Path $pkg 'electron') @('/XF', 'default_app.asar', 'debug.log')
    Copy-Item (Join-Path $PSScriptRoot 'setup-package.ps1') (Join-Path $pkg 'setup.ps1') -Force
    @"
@echo off
title Installation de Cybbig
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup.ps1"
if errorlevel 1 pause
"@ | Set-Content (Join-Path $pkg 'Installer Cybbig.cmd') -Encoding ASCII
    @"
CYBBIG $Version - poste local de cybersécurité défensive

Installation : double-cliquez sur « Installer Cybbig.cmd ».
  - Programme : %LOCALAPPDATA%\Programs\Cybbig
  - Données   : %APPDATA%\Cybbig (restent sur ce poste, jamais envoyées dans un cloud)
  - Raccourcis Bureau et menu Démarrer, désinstallation depuis Paramètres > Applications.

Aucune installation de Python ou de Node.js n'est nécessaire.
Assistant IA : installez Ollama (ollama.com) puis un modèle, par exemple « ollama pull qwen2.5-coder:7b ».
Mise à jour : relancez l'installation d'une version plus récente ; les données sont conservées.
"@ | Set-Content (Join-Path $pkg 'LISEZMOI.txt') -Encoding UTF8
    $zipOut = Join-Path $Release "$name.zip"
    if (Test-Path $zipOut) { Remove-Item $zipOut -Force }
    Push-Location $Release
    try { & tar.exe -a -c -f "$name.zip" $name; if ($LASTEXITCODE -ne 0) { throw 'Création du zip impossible.' } } finally { Pop-Location }
    Write-Host "    $zipOut ($([int]((Get-Item $zipOut).Length / 1MB)) Mo)" -ForegroundColor DarkGray
}

if ($SetupExe) {
    Step 'Setup.exe (electron-builder / NSIS)'
    Push-Location $Root
    try {
        if (-not (Test-Path (Join-Path $Root 'node_modules\electron-builder'))) {
            & $npm install --save-dev --no-audit --no-fund electron-builder@26.0.12 | Out-Null
            if ($LASTEXITCODE -ne 0) { throw 'Installation de electron-builder impossible.' }
        }
        $env:CSC_IDENTITY_AUTO_DISCOVERY = 'false'   # pas de certificat de signature
        & (Join-Path $Root 'node_modules\.bin\electron-builder.cmd') --win nsis --x64 --config electron-builder.yml --publish never
        if ($LASTEXITCODE -ne 0) { throw 'electron-builder a échoué.' }
    } finally { Pop-Location }
    Get-ChildItem (Join-Path $Release 'setup') -Filter '*.exe' | ForEach-Object { Write-Host "    $($_.FullName) ($([int]($_.Length / 1MB)) Mo)" -ForegroundColor DarkGray }
}

Write-Host ''
Write-Host '  Installateurs prêts dans release\' -ForegroundColor Green
exit 0
