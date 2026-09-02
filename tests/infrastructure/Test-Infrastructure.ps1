[CmdletBinding()]
param(
    [string[]]$ServiceName = @('Dnscache','Dhcp','NlaSvc')
)

$ErrorActionPreference = 'Stop'

$services = @(Get-Service -Name $ServiceName -ErrorAction SilentlyContinue)

$results = foreach ($service in $services) {
    [PSCustomObject]@{
        Service = $service.Name
        Status  = $service.Status
        Passed  = ($service.Status -eq 'Running')
    }
}

$results | Format-Table -AutoSize

if ($results.Count -eq 0 -or ($results.Passed -contains $false)) {
    exit 1
}
