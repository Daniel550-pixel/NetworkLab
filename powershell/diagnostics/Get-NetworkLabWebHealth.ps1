[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'

$connectivity = @(
    '127.0.0.1' | ForEach-Object {
        [PSCustomObject]@{
            target = $_
            ok = [bool](Test-Connection -ComputerName $_ -Count 1 -Quiet -ErrorAction SilentlyContinue)
        }
    }
)

$services = @(
    'Dnscache','Dhcp','NlaSvc' | ForEach-Object {
        $service = Get-Service -Name $_ -ErrorAction SilentlyContinue

        if ($service) {
            [PSCustomObject]@{
                name = $service.Name
                status = $service.Status.ToString()
                running = [bool]($service.Status -eq 'Running')
            }
        }
    }
)

[PSCustomObject]@{
    timestamp = (Get-Date).ToString('o')
    connectivity_ok = (@($connectivity | Where-Object { -not $_.ok }).Count -eq 0)
    connectivity = $connectivity
    services_total = $services.Count
    services_running = @($services | Where-Object { $_.running }).Count
    services_ok = (@($services | Where-Object { -not $_.running }).Count -eq 0)
    powershell = $PSVersionTable.PSVersion.ToString()
    python_available = [bool](Get-Command python -ErrorAction SilentlyContinue)
} | ConvertTo-Json -Depth 8
