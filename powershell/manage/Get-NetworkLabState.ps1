[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'

$adapters = @(Get-NetAdapter -ErrorAction SilentlyContinue |
    Select-Object Name, Status, LinkSpeed, MacAddress)

$ip = @(Get-NetIPConfiguration -ErrorAction SilentlyContinue | ForEach-Object {
    [PSCustomObject]@{
        interface = $_.InterfaceAlias
        ipv4 = @($_.IPv4Address | ForEach-Object { $_.IPv4Address }) -join ', '
        gateway = @($_.IPv4DefaultGateway | ForEach-Object { $_.NextHop }) -join ', '
        dns = @($_.DNSServer.ServerAddresses) -join ', '
    }
} | Where-Object { $_.ipv4 -or $_.gateway -or $_.dns })

$connectivity = @(
    '127.0.0.1' | ForEach-Object {
        $target = $_
        $watch = [Diagnostics.Stopwatch]::StartNew()
        $ok = Test-Connection -ComputerName $target -Count 1 -Quiet -ErrorAction SilentlyContinue
        $watch.Stop()

        [PSCustomObject]@{
            target = $target
            ok = [bool]$ok
            latency = if ($ok) { "$($watch.ElapsedMilliseconds) ms" } else { 'timeout' }
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
                startType = $service.StartType.ToString()
            }
        }
        else {
            [PSCustomObject]@{
                name = $_
                status = 'Not found'
                startType = 'Unknown'
            }
        }
    }
)

[PSCustomObject]@{
    project = 'NetworkLab'
    environment = 'stage-lab'
    timestamp = (Get-Date).ToString('o')
    adapters = $adapters
    ip = $ip
    connectivity = $connectivity
    services = $services
} | ConvertTo-Json -Depth 8
