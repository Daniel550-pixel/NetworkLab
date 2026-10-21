[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("InjectFault", "Detect", "Recover", "Verify")]
    [string]$Action
)

$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$statePath = Join-Path $repoRoot "config\simulation\incident-state.json"
$logPath = Join-Path $repoRoot "logs\incident-simulation.jsonl"

foreach ($directory in @((Split-Path $statePath -Parent), (Split-Path $logPath -Parent))) {
    if (-not (Test-Path -LiteralPath $directory)) {
        New-Item -ItemType Directory -Path $directory -Force | Out-Null
    }
}

if (Test-Path -LiteralPath $statePath) {
    try {
        $state = Get-Content -LiteralPath $statePath -Raw | ConvertFrom-Json
        if ([string]::IsNullOrWhiteSpace([string]$state.status)) {
            throw "State file does not contain a status field."
        }
    } catch {
        throw "Invalid incident state file '$statePath': $($_.Exception.Message)"
    }
} else {
    $state = [pscustomobject]@{
        status = "normal"
        scenario = "connectivity-loss"
        target = "simulated-network-node"
        updated_at = (Get-Date).ToString("o")
    }
}

$expected = @{
    InjectFault = "normal"
    Detect      = "fault_injected"
    Recover     = "detected"
    Verify      = "recovery"
}
if ([string]$state.status -ne $expected[$Action]) {
    throw "Action '$Action' requires state '$($expected[$Action])'; current state is '$($state.status)'."
}

$nextStatus = @{
    InjectFault = "fault_injected"
    Detect      = "detected"
    Recover     = "recovery"
    Verify      = "normal"
}
$eventType = @{
    InjectFault = "FAULT_INJECTED"
    Detect      = "DETECTED"
    Recover     = "RECOVERY"
    Verify      = "VERIFIED"
}

$state.status = $nextStatus[$Action]
$state.scenario = if ($state.scenario) { [string]$state.scenario } else { "connectivity-loss" }
$state.target = if ($state.target) { [string]$state.target } else { "simulated-network-node" }
$state.updated_at = (Get-Date).ToString("o")
$state | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $statePath -Encoding UTF8

$event = [ordered]@{
    timestamp = (Get-Date).ToString("o")
    event_type = $eventType[$Action]
    action = $Action
    status = $state.status
    scenario = $state.scenario
    target = $state.target
    simulation = $true
}
($event | ConvertTo-Json -Compress) | Add-Content -LiteralPath $logPath -Encoding UTF8
Write-Host "[$($event.event_type)] status=$($state.status) simulation=true"
