[CmdletBinding(SupportsShouldProcess)]
param(
    [Parameter(Mandatory = $false)]
    [string]$InterfaceAlias,

    [Parameter(Mandatory = $false)]
    [ValidateSet('Automatic','Manual')]
    [string]$DhcpMode = 'Automatic'
)

$ErrorActionPreference = 'Stop'

$configPath = Join-Path $PSScriptRoot '../../config/lab-config.json'
$config = Get-Content $configPath -Raw | ConvertFrom-Json

if (-not $config.safety.configuration_enabled) {
    throw 'Configuration changes are disabled in config/lab-config.json. Enable configuration_enabled only after the stage lab topology is defined.'
}

if (-not $config.safety.require_lab_scope) {
    throw 'Lab-scope safety requirement is disabled. Refusing to continue.'
}

if ([string]::IsNullOrWhiteSpace($InterfaceAlias)) {
    throw 'InterfaceAlias is required for any configuration operation.'
}

$adapter = Get-NetAdapter -Name $InterfaceAlias -ErrorAction Stop

if ($PSCmdlet.ShouldProcess($InterfaceAlias, "Set IPv4 configuration mode to $DhcpMode")) {
    if ($DhcpMode -eq 'Automatic') {
        Set-NetIPInterface -InterfaceAlias $InterfaceAlias -Dhcp Enabled
        Set-DnsClientServerAddress -InterfaceAlias $InterfaceAlias -ResetServerAddresses
    }
    else {
        throw 'Manual mode requires an explicitly documented stage-lab IP, gateway and DNS plan before implementation.'
    }
}

Get-NetIPConfiguration -InterfaceAlias $InterfaceAlias |
    Select-Object InterfaceAlias, IPv4Address, IPv4DefaultGateway, DNSServer |
    Format-List
