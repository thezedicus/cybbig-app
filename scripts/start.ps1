#requires -Version 5.1
[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

$npm = Get-Command npm.cmd -ErrorAction SilentlyContinue
if (-not $npm) { throw "npm.cmd est introuvable. Exécutez scripts\setup.ps1 après avoir installé Node.js." }

if (-not (Test-Path (Join-Path $Root 'node_modules\electron\dist\electron.exe'))) {
    Write-Host 'Binaire Electron manquant : exécutez scripts\setup.ps1.' -ForegroundColor Red
    throw 'Electron n est pas installé.'
}

# Recompile l'interface si elle est absente ou plus ancienne que ses sources.
$distIndex = Join-Path $Root 'frontend\dist\index.html'
$needsBuild = -not (Test-Path $distIndex)
if (-not $needsBuild) {
    $builtAt = (Get-Item $distIndex).LastWriteTimeUtc
    $sources = @(Get-ChildItem (Join-Path $Root 'frontend\src') -Recurse -File) +
        @(Get-Item (Join-Path $Root 'frontend\index.html'))
    $needsBuild = [bool]($sources | Where-Object { $_.LastWriteTimeUtc -gt $builtAt } | Select-Object -First 1)
}
if ($needsBuild) {
    Write-Host 'Interface modifiée : compilation...' -ForegroundColor Yellow
    & $npm run build
    if ($LASTEXITCODE -ne 0) { throw 'La compilation du frontend a échoué.' }
}

Write-Host 'Démarrage de Cybbig...' -ForegroundColor Cyan
& $npm start
