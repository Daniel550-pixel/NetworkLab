param(
    [int]$Port = 3000
)

$ErrorActionPreference = 'Continue'
$Root = $PSScriptRoot
$WebRoot = Join-Path $Root 'web'
$Index = Join-Path $WebRoot 'index.html'

if (-not (Test-Path $Index)) { throw "Web UI not found: $Index" }

$listener = [System.Net.HttpListener]::new()
$listener.Prefixes.Add("http://localhost:$Port/")
$listener.Start()

Write-Host ""
Write-Host "NETWORKLAB LOCAL WEBAPP" -ForegroundColor Cyan
Write-Host "URL: http://localhost:$Port" -ForegroundColor Green
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
    $targets = @('127.0.0.1')
    $connectivity = @($targets | ForEach-Object {
        $target=$_
        $sw=[Diagnostics.Stopwatch]::StartNew()
        $ok=Test-Connection -ComputerName $target -Count 1 -Quiet -ErrorAction SilentlyContinue
        $sw.Stop()
        [pscustomobject]@{target=$target;address=$target;ok=[bool]$ok;latency=if($ok){"$($sw.ElapsedMilliseconds) ms"}else{"timeout"}}
    })
    $serviceNames=@('Dnscache','Dhcp','NlaSvc')
    $services=@($serviceNames | ForEach-Object {
        $s=Get-Service -Name $_ -ErrorAction SilentlyContinue
        if($s){[pscustomobject]@{name=$s.Name;status=$s.Status.ToString();startType=$s.StartType.ToString()}}
        else{[pscustomobject]@{name=$_;status='Not found';startType='Unknown'}}
    })
    [pscustomobject]@{
        project='NetworkLab'
        environment='stage-lab'
        computer=$env:COMPUTERNAME
        timestamp=(Get-Date).ToString('o')
        scope=[pscustomobject]@{model='software-only';physical_hardware_required=$false;production_network_allowed=$false}
        safety=[pscustomobject]@{configuration_enabled=$false;require_lab_scope=$true}
        adapters=$adapters
        ip=$ip
        connectivity=$connectivity
        services=$services
        diagnostics=[pscustomobject]@{
            powershell=$PSVersionTable.PSVersion.ToString()
            python=([bool](Get-Command python -ErrorAction SilentlyContinue))
            adapterCount=$adapters.Count
            ipv4Count=$ip.Count
        }
    }
}

function Send-Json($context,$object,$statusCode=200) {
    $bytes=[Text.Encoding]::UTF8.GetBytes(($object|ConvertTo-Json -Depth 8))
    $context.Response.StatusCode=$statusCode
    $context.Response.ContentType='application/json; charset=utf-8'
    $context.Response.ContentLength64=$bytes.Length
    $context.Response.OutputStream.Write($bytes,0,$bytes.Length)
    $context.Response.Close()
}

function Send-File($context,$path,$type) {
    $bytes=[IO.File]::ReadAllBytes($path)
    $context.Response.StatusCode=200
    $context.Response.ContentType=$type
    $context.Response.ContentLength64=$bytes.Length
    $context.Response.OutputStream.Write($bytes,0,$bytes.Length)
    $context.Response.Close()
}

try {
    while($listener.IsListening) {
        $context=$listener.GetContext()
        try {
            switch -Regex ($context.Request.Url.AbsolutePath) {
                '^/$' { Send-File $context $Index 'text/html; charset=utf-8'; continue }
                '^/api/state$' { Send-Json $context (Get-State); continue }
                '^/api/health$' {
                    $state=Get-State
                    $state.health='completed'
                    $state.healthTimestamp=(Get-Date).ToString('o')
                    Send-Json $context $state
                    continue
                }
                default { Send-Json $context ([pscustomobject]@{error='Not found'}) 404 }
            }
        } catch {
            Send-Json $context ([pscustomobject]@{error=$_.Exception.Message}) 500
        }
    }
} finally {
    $listener.Stop()
    $listener.Close()
}
