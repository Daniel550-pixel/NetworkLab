[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'

& (Join-Path $PSScriptRoot 'Get-NetworkLabState.ps1') |
    ConvertFrom-Json |
    ConvertTo-Json -Depth 8
