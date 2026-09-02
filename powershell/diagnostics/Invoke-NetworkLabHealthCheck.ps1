[CmdletBinding()]
param(
    [string[]]$Target = @('127.0.0.1')
)

$ErrorActionPreference = 'Stop'

Write-Host '=== NetworkLab Health Check ==='
Write-Host "Timestamp: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Write-Host ''

Write-Host '--- Network configuration ---'
& (Join-Path $PSScriptRoot 'Test-NetworkLabConfiguration.ps1')
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host ''
Write-Host '--- Connectivity ---'
& (Join-Path $PSScriptRoot 'Test-NetworkLabConnectivity.ps1') -Target $Target
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host ''
Write-Host '--- Infrastructure services ---'
& (Join-Path $PSScriptRoot '../manage/Get-NetworkLabServices.ps1')

Write-Host ''
Write-Host 'Health check completed.'
