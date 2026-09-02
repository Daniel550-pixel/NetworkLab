[CmdletBinding()]
param(
    [string]$OutputPath = ''
)

$ErrorActionPreference = 'Stop'

$timestamp = Get-Date -Format 'yyyy-MM-ddTHH:mm:ssK'
$adapters = @(Get-NetAdapter | Select-Object Name, InterfaceDescription, Status, LinkSpeed, MacAddress)
$ip = @(Get-NetIPConfiguration | Select-Object InterfaceAlias, IPv4Address, IPv4DefaultGateway, DNSServer)
$services = @(Get-Service -Name 'Dnscache','Dhcp','NlaSvc' -ErrorAction SilentlyContinue |
    Select-Object Name, DisplayName, Status, StartType)

$evidence = [PSCustomObject]@{
    Project = 'NetworkLab'
    Environment = 'stage-lab'
    GeneratedAt = $timestamp
    Scope = 'software-only'
    NetworkAdapters = $adapters
    IPConfiguration = $ip
    InfrastructureServices = $services
}

$json = $evidence | ConvertTo-Json -Depth 6

if ([string]::IsNullOrWhiteSpace($OutputPath)) {
    $json
}
else {
    $directory = Split-Path -Parent $OutputPath
    if ($directory -and -not (Test-Path $directory)) {
        New-Item -ItemType Directory -Path $directory -Force | Out-Null
    }
    Set-Content -Path $OutputPath -Value $json -Encoding UTF8
    Write-Host "Evidence written to $OutputPath"
}
