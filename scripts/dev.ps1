#requires -Version 5.1
[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$npm = Get-Command npm.cmd -ErrorAction SilentlyContinue
if (-not $npm) { throw 'npm.cmd est introuvable.' }

$vite = Start-Process -FilePath $npm.Source `
    -ArgumentList @('run', 'dev') `
    -WorkingDirectory (Join-Path $Root 'frontend') -PassThru

try {
    Write-Host 'Interface Vite : http://127.0.0.1:5173' -ForegroundColor Cyan
    Start-Sleep -Seconds 3
    $env:CYBBIG_DEV_URL = 'http://127.0.0.1:5173'
    Push-Location $Root
    try { & $npm start -- --dev }
    finally { Pop-Location }
}
finally {
    if ($vite -and -not $vite.HasExited) {
        & taskkill /pid $vite.Id /T /F | Out-Null
    }
}
