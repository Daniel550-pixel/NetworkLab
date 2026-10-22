[CmdletBinding()]
param()

$ErrorActionPreference = "Continue"
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$LogDir = Join-Path $ProjectRoot "logs"
$LogFile = Join-Path $LogDir "networklab-autorecovery.log"
$EnsureScript = Join-Path $PSScriptRoot "Ensure-NetworkLabWebApps.ps1"
New-Item -ItemType Directory -Path $LogDir -Force | Out-Null

if (-not (Test-Path -LiteralPath $EnsureScript -PathType Leaf)) {
    Add-Content -LiteralPath $LogFile -Encoding UTF8 -Value "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') FATAL Herstelscript ontbreekt: $EnsureScript"
    exit 2
}

$Mutex = New-Object System.Threading.Mutex($false, "Local\NetworkLabAutoRecovery")
$OwnsMutex = $false
try {
    try { $OwnsMutex = $Mutex.WaitOne(0) }
    catch [System.Threading.AbandonedMutexException] { $OwnsMutex = $true }

    if (-not $OwnsMutex) { exit 0 }

    while ($true) {
        try {
            & $EnsureScript
        } catch {
            Add-Content -LiteralPath $LogFile -Encoding UTF8 -Value "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') SUPERVISOR ERROR: $($_.Exception.Message)"
        }
        Start-Sleep -Seconds 60
    }
} finally {
    if ($OwnsMutex) { $Mutex.ReleaseMutex() }
    $Mutex.Dispose()
}
