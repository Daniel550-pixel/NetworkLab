$ErrorActionPreference = "Continue"

$Mutex = New-Object System.Threading.Mutex($false, "Local\NetworkLabAutoRecovery")
$OwnsMutex = $false

try {
    try {
        $OwnsMutex = $Mutex.WaitOne(0)
    } catch [System.Threading.AbandonedMutexException] {
        $OwnsMutex = $true
    }

    if (-not $OwnsMutex) {
        exit 0
    }

    $Root = "C:\Users\Daan Salden\Downloads\NetworkLab"
    $EnsureScript = Join-Path $Root "powershell\diagnostics\Ensure-NetworkLabWebApps.ps1"
    $LogFile = Join-Path $Root "logs\networklab-autorecovery.log"

    while ($true) {
        try {
            & $EnsureScript
        } catch {
            Add-Content -LiteralPath $LogFile -Encoding UTF8 `
                -Value "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') SUPERVISOR ERROR: $($_.Exception.Message)"
        }

        Start-Sleep -Seconds 60
    }
} finally {
    if ($OwnsMutex) {
        $Mutex.ReleaseMutex()
    }
    $Mutex.Dispose()
}
