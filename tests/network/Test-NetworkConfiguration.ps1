[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'

$adapters = @(Get-NetAdapter)
$configurations = @(Get-NetIPConfiguration)

$upAdapters = @($adapters | Where-Object Status -eq 'Up')
$configuredIPv4 = @($configurations | Where-Object IPv4Address)

[PSCustomObject]@{
    AdapterCount       = $adapters.Count
    UpAdapterCount     = $upAdapters.Count
    IPv4Configured     = $configuredIPv4.Count
    NetworkStateValid  = ($adapters.Count -gt 0 -and $upAdapters.Count -gt 0 -and $configuredIPv4.Count -gt 0)
} | Format-List

if ($adapters.Count -eq 0 -or $upAdapters.Count -eq 0 -or $configuredIPv4.Count -eq 0) {
    exit 1
}
