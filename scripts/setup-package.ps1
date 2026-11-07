#requires -Version 5.1
<#
  Installe (ou met à jour) Cybbig pour l'utilisateur courant à partir d'un paquet préparé :
    <paquet>\app       application (backend + Python embarqué + interface)
    <paquet>\electron  moteur de bureau (fichiers Electron d'origine)

  Programme : %LOCALAPPDATA%\Programs\Cybbig — Données : %APPDATA%\Cybbig\data (jamais écrasées).
  Copié dans le paquet autonome sous le nom setup.ps1 ; aussi utilisé par scripts\install.ps1.
#>
[CmdletBinding()]
param(
    [string]$AppSource = (Join-Path $PSScriptRoot 'app'),
    [string]$ElectronSource = (Join-Path $PSScriptRoot 'electron'),
    [string]$InstallDir = (Join-Path $env:LOCALAPPDATA 'Programs\Cybbig'),
    [string]$MigrateFrom = '',
    [switch]$NoLaunch
)

$ErrorActionPreference = 'Stop'
$AppDir = Join-Path $InstallDir 'resources\app'
$DataDir = Join-Path $env:APPDATA 'Cybbig\data'
$Version = (Get-Content (Join-Path $AppSource 'package.json') -Raw | ConvertFrom-Json).version

function Step($text) { Write-Host "  > $text" -ForegroundColor Cyan }
function Mirror($from, $to, [string[]]$extra = @()) {
    $options = @($from, $to, '/MIR', '/NFL', '/NDL', '/NJH', '/NJS', '/NP', '/R:2', '/W:1', '/XD', '__pycache__') + $extra
    & robocopy @options | Out-Null
    if ($LASTEXITCODE -ge 8) { throw "Copie impossible : $from -> $to (robocopy $LASTEXITCODE)" }
}

try {
    Write-Host ''
    Write-Host "  CYBBIG $Version - installation" -ForegroundColor Cyan
    Write-Host '  ----------------------------'
    foreach ($required in (Join-Path $AppSource 'desktop\main.js'), (Join-Path $ElectronSource 'electron.exe')) {
        if (-not (Test-Path $required)) { throw "Paquet incomplet : $required introuvable." }
    }

    Step 'Fermeture de Cybbig en cours d exécution'
    Get-Process Cybbig -ErrorAction SilentlyContinue | Stop-Process -Force -Confirm:$false
    Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
        Where-Object { $_.CommandLine -like '*uvicorn*app.main:app*' -and $_.ExecutablePath -like "$InstallDir*" } |
        ForEach-Object { Stop-Process -Id $_.ProcessId -Force -Confirm:$false -ErrorAction SilentlyContinue }
    # Electron lance plusieurs processus : on attend qu'ils soient tous fermés avant de remplacer les fichiers.
    for ($i = 0; $i -lt 40 -and (Get-Process Cybbig -ErrorAction SilentlyContinue); $i++) {
        Get-Process Cybbig -ErrorAction SilentlyContinue | Stop-Process -Force -Confirm:$false -ErrorAction SilentlyContinue
        Start-Sleep -Milliseconds 500
    }
    Start-Sleep -Milliseconds 800

    Step 'Moteur de bureau'
    Mirror $ElectronSource $InstallDir @('/XD', $AppDir, '/XF', 'Cybbig.exe', 'uninstall.ps1', 'default_app.asar')
    for ($attempt = 1; ; $attempt++) {
        try { Copy-Item (Join-Path $ElectronSource 'electron.exe') (Join-Path $InstallDir 'Cybbig.exe') -Force; break }
        catch { if ($attempt -ge 10) { throw } ; Start-Sleep -Seconds 1 }
    }
    Remove-Item (Join-Path $InstallDir 'electron.exe'), (Join-Path $InstallDir 'resources\default_app.asar') -Force -ErrorAction SilentlyContinue

    Step 'Application'
    # node_modules de l'interface (installé à la première recompilation) est conservé entre deux mises à jour.
    Mirror $AppSource $AppDir @('/XD', (Join-Path $AppDir 'frontend\node_modules'))

    Step 'Données utilisateur'
    New-Item -ItemType Directory -Force $DataDir | Out-Null
    $targetDb = Join-Path $DataDir 'cybbig.db'
    if ($MigrateFrom -and -not (Test-Path $targetDb) -and (Test-Path (Join-Path $MigrateFrom 'cybbig.db'))) {
        $py = Join-Path $AppDir 'backend\python\python.exe'
        & $py -c "import sqlite3,sys; s=sqlite3.connect(sys.argv[1]); d=sqlite3.connect(sys.argv[2]); s.backup(d); d.close(); s.close()" (Join-Path $MigrateFrom 'cybbig.db') $targetDb
        if ($LASTEXITCODE -ne 0) { throw 'Reprise de la base impossible.' }
        foreach ($sub in 'reports', 'backups') {
            if (Test-Path (Join-Path $MigrateFrom $sub)) { Mirror (Join-Path $MigrateFrom $sub) (Join-Path $DataDir $sub) }
        }
        Write-Host '    base existante reprise' -ForegroundColor DarkGray
    }

    $uninstall = Join-Path $InstallDir 'uninstall.ps1'
    @"
`$ErrorActionPreference = 'SilentlyContinue'
Get-Process Cybbig | Stop-Process -Force
Start-Sleep -Milliseconds 800
Remove-Item (Join-Path ([Environment]::GetFolderPath('Desktop')) 'Cybbig.lnk') -Force
Remove-Item (Join-Path ([Environment]::GetFolderPath('Programs')) 'Cybbig.lnk') -Force
Remove-Item 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\Cybbig' -Recurse -Force
Set-Location `$env:TEMP
Remove-Item '$InstallDir' -Recurse -Force
# Les données (%APPDATA%\Cybbig) sont conservées volontairement.
"@ | Set-Content $uninstall -Encoding UTF8

    Step 'Raccourcis Bureau et menu Démarrer'
    $exe = Join-Path $InstallDir 'Cybbig.exe'
    $icon = Join-Path $AppDir 'desktop\icon.ico'
    $shell = New-Object -ComObject WScript.Shell
    foreach ($folder in [Environment]::GetFolderPath('Desktop'), [Environment]::GetFolderPath('Programs')) {
        $lnk = $shell.CreateShortcut((Join-Path $folder 'Cybbig.lnk'))
        $lnk.TargetPath = $exe
        $lnk.Arguments = ''
        $lnk.WorkingDirectory = $InstallDir
        $lnk.IconLocation = "$icon,0"
        $lnk.Description = 'Cybbig — poste de cybersécurité défensive'
        $lnk.WindowStyle = 1
        $lnk.Save()
    }

    $key = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\Cybbig'
    New-Item -Path $key -Force | Out-Null
    $size = [int]((Get-ChildItem $InstallDir -Recurse -File | Measure-Object Length -Sum).Sum / 1KB)
    $props = @{
        DisplayName = 'Cybbig'; DisplayVersion = $Version; Publisher = 'Cybbig'; DisplayIcon = $icon
        InstallLocation = $InstallDir; EstimatedSize = $size; NoModify = 1; NoRepair = 1
        UninstallString = "powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$uninstall`""
    }
    foreach ($name in $props.Keys) {
        $type = if ($props[$name] -is [int]) { 'DWord' } else { 'String' }
        New-ItemProperty -Path $key -Name $name -Value $props[$name] -PropertyType $type -Force | Out-Null
    }
    & "$env:SystemRoot\System32\ie4uinit.exe" -show 2>$null

    Write-Host ''
    Write-Host "  Cybbig $Version installé dans $InstallDir" -ForegroundColor Green
    Write-Host "  Données : $DataDir" -ForegroundColor DarkGray
    if (-not $NoLaunch) { Start-Process $exe -WorkingDirectory $InstallDir }
    exit 0
}
catch {
    Write-Host ''
    Write-Host "  Échec de l'installation : $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
