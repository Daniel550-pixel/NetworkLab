[CmdletBinding()]
param(
    [string[]]$Target = @('127.0.0.1')
)

$ErrorActionPreference = 'Stop'

$timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
$connectivity = foreach ($hostName in $Target) {
    [PSCustomObject]@{
        Target = $hostName
        Reachable = Test-Connection -ComputerName $hostName -Count 2 -Quiet
    }
}

$adapters = @(Get-NetAdapter)
$ip = @(Get-NetIPConfiguration)

$result = [PSCustomObject]@{
    Timestamp = $timestamp
    Connectivity = $connectivity
    AdaptersUp = @($adapters | Where-Object Status -eq 'Up').Count
    AdapterTotal = $adapters.Count
    IPv4Configured = @($ip | Where-Object IPv4Address).Count
}

$result | ConvertTo-Json -Depth 6
