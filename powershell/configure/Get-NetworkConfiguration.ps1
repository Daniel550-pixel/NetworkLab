[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'

$adapters = Get-NetAdapter |
    Select-Object Name, InterfaceDescription, Status, MacAddress, LinkSpeed

$configurations = Get-NetIPConfiguration |
    Select-Object InterfaceAlias,
        @{Name='IPv4';Expression={($_.IPv4Address | ForEach-Object IPAddress) -join ', '}},
        @{Name='Gateway';Expression={($_.IPv4DefaultGateway | ForEach-Object NextHop) -join ', '}},
        @{Name='DNS';Expression={($_.DNSServer.ServerAddresses) -join ', '}}

[PSCustomObject]@{
    Timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    Adapters  = $adapters
    IPConfig  = $configurations
} | ConvertTo-Json -Depth 5
