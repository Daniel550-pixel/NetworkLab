[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'

$results = @()

foreach ($adapter in Get-NetAdapter) {
    $results += [PSCustomObject]@{
        Component = 'Network Adapter'
        Name      = $adapter.Name
        Status    = $adapter.Status
        Healthy   = ($adapter.Status -eq 'Up')
        Detail    = $adapter.InterfaceDescription
    }
}

foreach ($config in Get-NetIPConfiguration) {
    $ipv4 = $config.IPv4Address | Select-Object -First 1
    $gateway = $config.IPv4DefaultGateway | Select-Object -First 1

    $results += [PSCustomObject]@{
        Component = 'IPv4 Configuration'
        Name      = $config.InterfaceAlias
        Status    = if ($ipv4) { 'Configured' } else { 'Missing' }
        Healthy   = [bool]$ipv4
        Detail    = if ($ipv4) { $ipv4.IPAddress } else { 'No IPv4 address detected' }
    }

    $results += [PSCustomObject]@{
        Component = 'Default Gateway'
        Name      = $config.InterfaceAlias
        Status    = if ($gateway) { 'Configured' } else { 'Missing' }
        Healthy   = [bool]$gateway
        Detail    = if ($gateway) { $gateway.NextHop } else { 'No IPv4 gateway detected' }
    }
}

$results | Format-Table -AutoSize
