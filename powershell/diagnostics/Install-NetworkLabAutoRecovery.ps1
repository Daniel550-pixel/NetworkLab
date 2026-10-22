$ErrorActionPreference = "Stop"
$Root = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$Supervisor = Join-Path $PSScriptRoot "Run-NetworkLabAutoRecovery.ps1"

if (-not (Test-Path $Supervisor -PathType Leaf)) {
    throw "Bewakingsscript ontbreekt: $Supervisor"
}

$Startup = [Environment]::GetFolderPath("Startup")
$Launcher = Join-Path $Startup "NetworkLab-AutoRecovery.vbs"
$PowerShell = "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe"

$Content = @"
Set shell = CreateObject("WScript.Shell")
shell.Run """$PowerShell"" -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File ""$Supervisor""", 0, False
"@

Set-Content -LiteralPath $Launcher -Value $Content -Encoding ASCII
Write-Host "Opstartbestand aangemaakt: $Launcher"
