#requires -Version 5.1
[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$installer = Join-Path $env:TEMP ("OllamaSetup-" + [Guid]::NewGuid().ToString() + ".exe")
$url = 'https://ollama.com/download/OllamaSetup.exe'

Write-Host 'Téléchargement de l installateur Ollama...' -ForegroundColor Cyan
Invoke-WebRequest -Uri $url -OutFile $installer -UseBasicParsing
if (-not (Test-Path $installer)) { throw 'Le téléchargement a échoué.' }

Write-Host 'Lancement de l installateur. Suivez les instructions à l écran.' -ForegroundColor Yellow
Start-Process -FilePath $installer -Wait

$ollama = Get-Command ollama -ErrorAction SilentlyContinue
if (-not $ollama) {
    $candidates = @(
        (Join-Path $env:LOCALAPPDATA 'Programs\Ollama\ollama.exe'),
        'C:\Program Files\Ollama\ollama.exe'
    )
    $found = $candidates | Where-Object { Test-Path $_ } | Select-Object -First 1
    if ($found) { Write-Host "Ollama installé : $found" -ForegroundColor Green }
    else { Write-Host 'Ollama ne semble pas être dans le PATH. Redémarrez le terminal après installation.' -ForegroundColor Yellow }
} else {
    & ollama --version
}
Write-Host 'Terminé. Vous pouvez fermer cette fenêtre.' -ForegroundColor Green
