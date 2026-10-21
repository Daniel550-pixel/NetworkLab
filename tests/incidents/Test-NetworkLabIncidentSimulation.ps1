$ErrorActionPreference = "Stop"
$root = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$statePath = Join-Path $root "config\simulation\incident-state.json"
$incidentLog = Join-Path $root "logs\incident-simulation.jsonl"
$detectionLog = Join-Path $root "logs\monitoring-detection.jsonl"
$cursorPath = Join-Path $root "config\simulation\monitoring-cursor.json"
$feedLog = Join-Path $root "logs\monitoring-feed.log"

$paths = @($statePath, $incidentLog, $detectionLog, $cursorPath, $feedLog)
$backup = @{}
foreach ($path in $paths) {
    if (Test-Path -LiteralPath $path) {
        $backup[$path] = [pscustomobject]@{ Exists = $true; Content = [System.IO.File]::ReadAllBytes($path) }
    } else {
        $backup[$path] = [pscustomobject]@{ Exists = $false; Content = $null }
    }
}

function Assert-True([bool]$Condition, [string]$Message) {
    if (-not $Condition) { throw "ASSERTION FAILED: $Message" }
}

try {
    $configDir = Split-Path $statePath -Parent
    $logDir = Split-Path $incidentLog -Parent
    New-Item -ItemType Directory -Path $configDir -Force | Out-Null
    New-Item -ItemType Directory -Path $logDir -Force | Out-Null
    foreach ($path in @($incidentLog, $detectionLog, $feedLog)) {
        if (Test-Path -LiteralPath $path) { Remove-Item -LiteralPath $path -Force }
    }
    @{ status = "normal"; scenario = "connectivity-loss"; target = "ci-test-node"; updated_at = (Get-Date).ToString("o") } |
        ConvertTo-Json | Set-Content -LiteralPath $statePath -Encoding UTF8
    @{ last_status = "normal"; updated_at = (Get-Date).ToString("o") } |
        ConvertTo-Json | Set-Content -LiteralPath $cursorPath -Encoding UTF8

    $lifecycle = Join-Path $root "tests\incidents\Invoke-NetworkLabIncidentSimulation.ps1"
    $monitor = Join-Path $root "powershell\manage\Start-NetworkLabMonitoringFeed.ps1"
    & $lifecycle -Action InjectFault
    & $monitor -IntervalSeconds 1 -Iterations 1
    & $lifecycle -Action Detect
    & $lifecycle -Action Recover
    & $lifecycle -Action Verify

    $finalState = Get-Content -LiteralPath $statePath -Raw | ConvertFrom-Json
    Assert-True ($finalState.status -eq "normal") "Lifecycle did not return to normal."
    $events = @(Get-Content -LiteralPath $incidentLog | ForEach-Object { $_ | ConvertFrom-Json })
    $expected = @("FAULT_INJECTED", "DETECTED", "RECOVERY", "VERIFIED")
    foreach ($eventType in $expected) {
        Assert-True (@($events | Where-Object event_type -eq $eventType).Count -eq 1) "Missing or duplicate lifecycle event: $eventType"
    }
    $detections = @(Get-Content -LiteralPath $detectionLog | ForEach-Object { $_ | ConvertFrom-Json })
    Assert-True ($detections.Count -eq 1) "Expected exactly one monitoring detection."
    Assert-True ($detections[0].simulation -eq $true) "Detection must be marked as a simulation."

    $failedAsExpected = $false
    try {
        & $lifecycle -Action Recover
    } catch {
        $failedAsExpected = $true
    }
    Assert-True $failedAsExpected "Out-of-order Recover action was not rejected."
    Write-Host "PASS: lifecycle order, event logging, monitoring detection, recovery, and invalid-order guard."
}
finally {
    foreach ($path in $paths) {
        $entry = $backup[$path]
        if ($entry.Exists) {
            $parent = Split-Path $path -Parent
            if (-not (Test-Path -LiteralPath $parent)) { New-Item -ItemType Directory -Path $parent -Force | Out-Null }
            [System.IO.File]::WriteAllBytes($path, $entry.Content)
        } elseif (Test-Path -LiteralPath $path) {
            Remove-Item -LiteralPath $path -Force
        }
    }
}
