[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'

Write-Host '=== NetworkLab: Network State ==='

Get-NetAdapter |
    Select-Object Name, InterfaceDescription, Status, LinkSpeed, MacAddress |
    Format-Table -AutoSize

Write-Host "`n=== IP Configuration ==="

Get-NetIPConfiguration |
    Select-Object InterfaceAlias, IPv4Address, IPv4DefaultGateway, DNSServer |
    Format-List
