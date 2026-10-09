[CmdletBinding()]
param(
    [ValidateRange(1, 3600)]
    [int]$IntervalSeconds = 30,

    [ValidateRange(0, 1000000)]
    [int]$Iterations = 0
)

$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$statePath = Join-Path $repoRoot "config\simulation\incident-state.json"
$cursorPath = Join-Path $repoRoot "config\simulation\monitoring-cursor.json"
$eventLogPath = Join-Path $repoRoot "logs\monitoring-detection.jsonl"
$textLogPath = Join-Path $repoRoot "logs\monitoring-feed.log"

foreach ($directory in @((Split-Path $cursorPath -Parent), (Split-Path $eventLogPath -Parent))) {
    if (-not (Test-Path -LiteralPath $directory)) {
        New-Item -ItemType Directory -Path $directory -Force | Out-Null
    }
}
if (-not (Test-Path -LiteralPath $textLogPath)) {
    New-Item -ItemType File -Path $textLogPath -Force | Out-Null
}

$previousStatus = $null
if (Test-Path -LiteralPath $cursorPath) {
    try {
        $cursor = Get-Content -LiteralPath $cursorPath -Raw | ConvertFrom-Json
        $previousStatus = [string]$cursor.last_status
    } catch {
        Write-Warning "Monitoring cursor is invalid; starting without a previous state."
    }
}

$count = 0
do {
    $currentStatus = "unknown"
    if (Test-Path -LiteralPath $statePath) {
        try {
            $state = Get-Content -LiteralPath $statePath -Raw | ConvertFrom-Json
            if (-not [string]::IsNullOrWhiteSpace([string]$state.status)) {
                $currentStatus = [string]$state.status
            }
        } catch {
            $message = "$(Get-Date -Format o) ERROR Invalid state file: $($_.Exception.Message)"
            Add-Content -LiteralPath $textLogPath -Value $message -Encoding UTF8
            Write-Warning $message
        }
    }

    if (($currentStatus -eq "fault_injected") -and ($previousStatus -ne "fault_injected")) {
        $event = [ordered]@{
            timestamp = (Get-Date).ToString("o")
            event_type = "DETECTED"
            status = $currentStatus
            previous_status = $previousStatus
            scenario = "connectivity-loss"
            target = "simulated-network-node"
            simulation = $true
        }
        ($event | ConvertTo-Json -Compress) | Add-Content -LiteralPath $eventLogPath -Encoding UTF8
        $message = "$(Get-Date -Format o) DETECTED simulation=true scenario=connectivity-loss target=simulated-network-node"
        Add-Content -LiteralPath $textLogPath -Value $message -Encoding UTF8
        Write-Host $message
    } else {
        Write-Host "[$(Get-Date -Format T)] status=$currentStatus"
    }

    @{ last_status = $currentStatus; updated_at = (Get-Date).ToString("o") } |
        ConvertTo-Json | Set-Content -LiteralPath $cursorPath -Encoding UTF8
    $previousStatus = $currentStatus
    $count++

    if (($Iterations -eq 0) -or ($count -lt $Iterations)) {
        Start-Sleep -Seconds $IntervalSeconds
    }
} while (($Iterations -eq 0) -or ($count -lt $Iterations))
