[CmdletBinding(SupportsShouldProcess)]
param(
    [string]$NetworkName = "NetworkLab-Lab",
    [string]$HostAddress = "192.168.77.1",
    [string]$NetworkMask = "255.255.255.0",
    [string]$DhcpLower = "192.168.77.100",
    [string]$DhcpUpper = "192.168.77.200"
)

$ErrorActionPreference = "Stop"

function Resolve-VBoxManage {
    $cmd = Get-Command VBoxManage.exe -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }

    $candidates = @(
        "$env:ProgramFiles\Oracle\VirtualBox\VBoxManage.exe",
        "$env:ProgramFiles\VirtualBox\VBoxManage.exe"
    )

    foreach ($candidate in $candidates) {
        if (Test-Path $candidate) { return $candidate }
    }

    throw "VBoxManage.exe was not found. Install VirtualBox before creating the NetworkLab virtual network."
}

$VBoxManage = Resolve-VBoxManage
Write-Host "NETWORKLAB VIRTUAL NETWORK" -ForegroundColor Cyan
Write-Host "Isolation: host-only (no physical LAN / Internet bridge)" -ForegroundColor DarkGray
Write-Host "Network: $NetworkName" -ForegroundColor DarkGray
Write-Host "Host: $HostAddress/$NetworkMask" -ForegroundColor DarkGray
Write-Host ""

$existing = & $VBoxManage list hostonlyifs | Out-String
$adapterName = $null

# Reuse an existing host-only adapter already carrying the lab gateway address.
$blocks = [regex]::Matches($existing, "(?ms)(?=^Name:).+?(?=\r?\n\r?\n|\z)")
foreach ($block in $blocks) {
    if ($block.Value -match ("(?m)^IPAddress:\s+" + [regex]::Escape($HostAddress) + "\s*$")) {
        $nameMatch = [regex]::Match($block.Value, "(?m)^Name:\s+(.+)$")
        if ($nameMatch.Success) { $adapterName = $nameMatch.Groups[1].Value.Trim(); break }
    }
}

if (-not $adapterName) {
    if (-not $PSCmdlet.ShouldProcess($NetworkName, "Create isolated VirtualBox host-only network")) {
        return
    }

    $createOutput = & $VBoxManage hostonlyif create 2>&1 | Out-String
    $createdMatch = [regex]::Match($createOutput, 'Name:s+(.+)')
    if ($createdMatch.Success) {
        $adapterName = $createdMatch.Groups[1].Value.Trim()
    }

    if (-not $adapterName) {
        $interfaces = & $VBoxManage list hostonlyifs | Out-String
        $names = [regex]::Matches($interfaces, '(?m)^Name:s+(.+)$')
        if ($names.Count -gt 0) {
            $adapterName = $names[$names.Count - 1].Groups[1].Value.Trim()
        }
    }
}

if (-not $adapterName) {
    throw "VirtualBox created no host-only adapter."
}

Write-Host "Host-only adapter: $adapterName" -ForegroundColor Green

if ($PSCmdlet.ShouldProcess($adapterName, "Configure $HostAddress/$NetworkMask")) {
    & $VBoxManage hostonlyif ipconfig $adapterName --ip $HostAddress --netmask $NetworkMask
    if ($LASTEXITCODE -ne 0) { throw "Failed to configure the host-only adapter." }
}

$dhcpList = & $VBoxManage list dhcpservers | Out-String
$dhcpExists = $dhcpList -match [regex]::Escape($NetworkName)

if (-not $dhcpExists -and $PSCmdlet.ShouldProcess($NetworkName, "Create isolated DHCP scope $DhcpLower-$DhcpUpper")) {
    & $VBoxManage dhcpserver add --ifname $adapterName --ip 192.168.77.2 --netmask $NetworkMask --lowerip $DhcpLower --upperip $DhcpUpper --enable
    if ($LASTEXITCODE -ne 0) { throw "Failed to create the VirtualBox DHCP server." }
}

Write-Host ""
Write-Host "Virtual network ready." -ForegroundColor Green
Write-Host "Host endpoint: $HostAddress" -ForegroundColor Green
Write-Host "DHCP range: $DhcpLower - $DhcpUpper" -ForegroundColor Green
Write-Host "Traffic is isolated from the physical LAN and Internet." -ForegroundColor Green
