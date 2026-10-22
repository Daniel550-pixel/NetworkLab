[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$Supervisor = Join-Path $PSScriptRoot "Run-NetworkLabAutoRecovery.ps1"
$LogDir = Join-Path $Root "logs"
$Log = Join-Path $LogDir "networklab-autorecovery.log"
$PSExe = Join-Path $env:SystemRoot "System32\WindowsPowerShell\v1.0\powershell.exe"
New-Item -ItemType Directory -Path $LogDir -Force | Out-Null

if (-not (Test-Path -LiteralPath $Supervisor -PathType Leaf)) { throw "Bewakingsscript ontbreekt: $Supervisor" }
if (-not (Test-Path -LiteralPath $PSExe -PathType Leaf)) { throw "Windows PowerShell is niet gevonden: $PSExe" }

$Running = Get-CimInstance Win32_Process | Where-Object { $_.Name -ieq "powershell.exe" -and $_.CommandLine -match "Run-NetworkLabAutoRecovery\.ps1" }
if (-not $Running) {
    $Arguments = "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$Supervisor`""
    Start-Process -FilePath $PSExe -ArgumentList $Arguments -WorkingDirectory $Root -WindowStyle Hidden
    Add-Content -LiteralPath $Log -Encoding UTF8 -Value "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') WATCHDOG: supervisor gestart"
}
