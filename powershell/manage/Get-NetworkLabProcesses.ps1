[CmdletBinding()]
param(
    [int]$Top = 10
)

$ErrorActionPreference = 'Stop'

Get-Process |
    Sort-Object CPU -Descending |
    Select-Object -First $Top Name, Id, CPU, WorkingSet64 |
    Format-Table -AutoSize
