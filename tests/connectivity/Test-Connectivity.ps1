[CmdletBinding()]
param(
    [string[]]$Target = @('127.0.0.1')
)

$ErrorActionPreference = 'Stop'

$results = foreach ($hostName in $Target) {
    $success = Test-Connection -ComputerName $hostName -Count 2 -Quiet
    [PSCustomObject]@{
        Target = $hostName
        Passed = $success
    }
}

$results | Format-Table -AutoSize

if ($results.Passed -contains $false) {
    exit 1
}
