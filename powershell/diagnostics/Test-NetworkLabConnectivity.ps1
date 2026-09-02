[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [string[]]$Target = @('127.0.0.1')
)

$ErrorActionPreference = 'Stop'

$results = foreach ($hostName in $Target) {
    $reachable = Test-Connection -ComputerName $hostName -Count 2 -Quiet

    [PSCustomObject]@{
        Target    = $hostName
        Reachable = $reachable
        Timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    }
}

$results | Format-Table -AutoSize
