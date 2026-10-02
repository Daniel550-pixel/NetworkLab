$ErrorActionPreference = "Stop"

$cmd = Get-Command VBoxManage.exe -ErrorAction SilentlyContinue
if (-not $cmd) {
    $candidates = @(
        "$env:ProgramFiles\Oracle\VirtualBox\VBoxManage.exe",
        "$env:ProgramFiles\VirtualBox\VBoxManage.exe"
    )
    $path = $candidates | Where-Object { Test-Path $_ } | Select-Object -First 1
    if (-not $path) { throw "VBoxManage.exe was not found." }
} else {
    $path = $cmd.Source
}

Write-Host "=== NetworkLab Virtual Network ===" -ForegroundColor Cyan
& $path list hostonlyifs
Write-Host ""
Write-Host "=== VirtualBox DHCP Servers ===" -ForegroundColor Cyan
& $path list dhcpservers
