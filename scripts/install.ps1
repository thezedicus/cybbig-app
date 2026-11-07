#requires -Version 5.1
<#
  Installe (ou met à jour) Cybbig sur ce poste à partir des sources du projet.

  Prépare la copie autonome (build-installer.ps1 -StageOnly : interface compilée, Python embarqué)
  puis l'installe avec setup-package.ps1. À la première installation, la base de backend\data est reprise.
  Relancer ce script après chaque modification du code met l'installation à jour ; les données sont conservées.
#>
[CmdletBinding()]
param([switch]$NoLaunch)

$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot

& (Join-Path $PSScriptRoot 'build-installer.ps1') -StageOnly
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

$setupArgs = @{
    AppSource      = Join-Path $Root 'release\stage\app'
    ElectronSource = Join-Path $Root 'node_modules\electron\dist'
    MigrateFrom    = Join-Path $Root 'backend\data'
}
if ($NoLaunch) { $setupArgs.NoLaunch = $true }
& (Join-Path $PSScriptRoot 'setup-package.ps1') @setupArgs
exit $LASTEXITCODE
