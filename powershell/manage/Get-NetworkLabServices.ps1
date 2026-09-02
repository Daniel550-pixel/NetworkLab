[CmdletBinding()]
param(
    [string[]]$Name = @('Dnscache','Dhcp','NlaSvc')
)

$ErrorActionPreference = 'Stop'

Get-Service -Name $Name -ErrorAction SilentlyContinue |
    Select-Object Name, DisplayName, Status, StartType |
    Sort-Object Name |
    Format-Table -AutoSize
