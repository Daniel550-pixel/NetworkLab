param(
    [int]$Port = 3000
)

$ErrorActionPreference = 'Stop'
$Root = $PSScriptRoot
$Index = Join-Path $Root 'web\index.html'

if (-not (Test-Path $Index)) {
    throw "Web UI not found: $Index"
}

$listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Loopback, $Port)

try {
    $listener.Start()

    Write-Host ""
    Write-Host "NETWORKLAB LOCAL WEBAPP" -ForegroundColor Cyan
    Write-Host "URL: http://localhost:$Port" -ForegroundColor Green
    Write-Host "Listening on 127.0.0.1:$Port" -ForegroundColor DarkGray
    Write-Host "Press Ctrl+C to stop." -ForegroundColor DarkGray
    Write-Host ""

    function Get-State {
        $adapters = @(Get-NetAdapter -ErrorAction SilentlyContinue | Select-Object Name,Status,@{N='Speed';E={$_.LinkSpeed}},MacAddress)
        $ip = @(Get-NetIPConfiguration -ErrorAction SilentlyContinue | ForEach-Object {
            [pscustomobject]@{
                interface = $_.InterfaceAlias
                ipv4 = @($_.IPv4Address | ForEach-Object {$_.IPv4Address}) -join ', '
                gateway = @($_.IPv4DefaultGateway | ForEach-Object {$_.NextHop}) -join ', '
                dns = @($_.DNSServer.ServerAddresses) -join ', '
            }
        } | Where-Object {$_.ipv4 -or $_.gateway -or $_.dns})

        $connectivity = @(
            [pscustomobject]@{
                target='127.0.0.1'
                address='127.0.0.1'
                ok=$true
                latency='local'
            }
        )

        $services = @('Dnscache','Dhcp','NlaSvc') | ForEach-Object {
            $s = Get-Service -Name $_ -ErrorAction SilentlyContinue
            if ($s) {
                [pscustomobject]@{name=$s.Name;status=$s.Status.ToString();startType=$s.StartType.ToString()}
            } else {
                [pscustomobject]@{name=$_;status='Not found';startType='Unknown'}
            }
        }

        [pscustomobject]@{
            project='NetworkLab'
            environment='stage-lab'
            computer=$env:COMPUTERNAME
            timestamp=(Get-Date).ToString('o')
            scope=[pscustomobject]@{model='software-only';physical_hardware_required=$false;production_network_allowed=$false}
            safety=[pscustomobject]@{configuration_enabled=$false;require_lab_scope=$true}
            adapters=$adapters
            ip=$ip
            connectivity=@($connectivity)
            services=@($services)
            diagnostics=[pscustomobject]@{
                powershell=$PSVersionTable.PSVersion.ToString()
                python=([bool](Get-Command python -ErrorAction SilentlyContinue))
                adapterCount=$adapters.Count
                ipv4Count=$ip.Count
            }
        }
    }

    function Send-Response($stream, [int]$status, [string]$contentType, [byte[]]$body) {
        $reason = switch ($status) { 200 {'OK'} 404 {'Not Found'} 500 {'Internal Server Error'} default {'OK'} }
        $crlf = [char]13 + [char]10
        $header = "HTTP/1.1 $status $reason" + $crlf +
                  "Content-Type: $contentType" + $crlf +
                  "Content-Length: $($body.Length)" + $crlf +
                  "Connection: close" + $crlf +
                  "Access-Control-Allow-Origin: *" + $crlf + $crlf
        $headerBytes = [Text.Encoding]::ASCII.GetBytes($header)
        $stream.Write($headerBytes,0,$headerBytes.Length)
        if ($body.Length -gt 0) { $stream.Write($body,0,$body.Length) }
        $stream.Flush()
    }

    function Send-Json($stream, $object, [int]$status=200) {
        Send-Response $stream $status 'application/json; charset=utf-8' ([Text.Encoding]::UTF8.GetBytes(($object | ConvertTo-Json -Depth 10)))
    }

    function Send-File($stream, $path) {
        Send-Response $stream 200 'text/html; charset=utf-8' ([IO.File]::ReadAllBytes($path))
    }

    while ($true) {
        $client = $listener.AcceptTcpClient()
        $stream = $null
        $reader = $null

        try {
            $stream = $client.GetStream()
            $reader = [IO.StreamReader]::new($stream, [Text.Encoding]::ASCII, $false, 8192, $true)
            $requestLine = $reader.ReadLine()

            if ($requestLine) {
                while (($line = $reader.ReadLine()) -ne $null -and $line -ne '') {}

                $parts = $requestLine.Split(' ')
                $path = if ($parts.Count -ge 2) { $parts[1] } else { '/' }

                try {
                    switch -Regex ($path) {
                        '^/$' { Send-File $stream $Index; break }
                        '^/api/state$' { Send-Json $stream (Get-State); break }
                        '^/api/health$' {
                            $state = Get-State
                            $state.health = 'completed'
                            $state.healthTimestamp = (Get-Date).ToString('o')
                            Send-Json $stream $state
                            break
                        }
                        default { Send-Json $stream ([pscustomobject]@{error='Not found'}) 404 }
                    }
                } catch {
                    Send-Json $stream ([pscustomobject]@{error=$_.Exception.Message}) 500
                }
            }
        }
        finally {
            if ($reader) { $reader.Dispose() }
            if ($stream) { $stream.Dispose() }
            $client.Dispose()
        }
    }
}
finally {
    $listener.Stop()
}
