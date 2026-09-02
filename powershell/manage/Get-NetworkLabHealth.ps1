[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'

$adapters = @(Get-NetAdapter)
$ipConfigurations = @(Get-NetIPConfiguration)
$services = @(Get-Service -Name 'Dnscache','Dhcp','NlaSvc' -ErrorAction SilentlyContinue)

$upAdapters = @($adapters | Where-Object Status -eq 'Up')
$configuredIPv4 = @($ipConfigurations | Where-Object IPv4Address)
$runningServices = @($services | Where-Object Status -eq 'Running')

$health = [PSCustomObject]@{
    Timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    AdapterHealthy = ($adapters.Count -gt 0 -and $upAdapters.Count -gt 0)
    IPv4Configured = ($configuredIPv4.Count -gt 0)
    CoreServicesHealthy = ($services.Count -gt 0 -and $runningServices.Count -eq $services.Count)
    OverallHealthy = ($adapters.Count -gt 0 -and $upAdapters.Count -gt 0 -and $configuredIPv4.Count -gt 0 -and $services.Count -gt 0 -and $runningServices.Count -eq $services.Count)
}

$health | Format-List

if (-not $health.OverallHealthy) {
    exit 1
}
