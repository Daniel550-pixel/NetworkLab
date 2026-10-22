[CmdletBinding()]
param()
$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$PythonCommand = Get-Command python -ErrorAction SilentlyContinue
if (-not $PythonCommand) { throw "Python 3 is vereist. Installeer Python en controleer dat python in PATH staat." }
$Python = $PythonCommand.Source
$LogDir = Join-Path $ProjectRoot "logs"
New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
$Apps = @(
    @{ Name="CLIENT"; Port=8510; Url="http://127.0.0.1:8510/"; Directory=(Join-Path $ProjectRoot "apps\client"); Kind="static" },
    @{ Name="MGMT"; Port=8511; Url="http://127.0.0.1:8511/"; Directory=(Join-Path $ProjectRoot "apps\mgmt"); Kind="static" },
    @{ Name="INFRA"; Port=8512; Url="http://127.0.0.1:8512/"; Directory=(Join-Path $ProjectRoot "apps\infra"); Kind="infra" }
)
foreach ($App in $Apps) {
    if (-not (Test-Path -LiteralPath $App.Directory -PathType Container)) { throw "Applicatiemap ontbreekt: $($App.Directory)" }
    $Listener = Get-NetTCPConnection -State Listen -LocalPort $App.Port -ErrorAction SilentlyContinue
    if ($Listener) { throw "Poort $($App.Port) is al in gebruik. Er is niets gestart; controleer de listener voordat je opnieuw probeert." }
}
$Started = [System.Collections.Generic.List[object]]::new()
try {
    foreach ($App in $Apps) {
        $OutLog = Join-Path $LogDir ("networklab-" + $App.Name.ToLowerInvariant() + ".out.log")
        $ErrLog = Join-Path $LogDir ("networklab-" + $App.Name.ToLowerInvariant() + ".err.log")
        if ($App.Kind -eq "infra") {
            $Arguments = @('"' + (Join-Path $App.Directory "server.py") + '"')
        } else {
            $Arguments = @("-m", "http.server", [string]$App.Port, "--bind", "127.0.0.1", "--directory", ('"' + $App.Directory + '"'))
        }
        $Process = Start-Process -FilePath $Python -ArgumentList $Arguments -WorkingDirectory $ProjectRoot -WindowStyle Hidden -RedirectStandardOutput $OutLog -RedirectStandardError $ErrLog -PassThru
        $Started.Add([pscustomobject]@{ Name=$App.Name; PID=$Process.Id; Port=$App.Port; URL=$App.Url }) | Out-Null
    }
    Start-Sleep -Seconds 2
    $Results = foreach ($App in $Started) {
        $Proc = Get-Process -Id $App.PID -ErrorAction SilentlyContinue
        $HttpStatus = "NOT TESTED"
        try {
            $Response = Invoke-WebRequest -Uri $App.URL -TimeoutSec 3 -UseBasicParsing
            $HttpStatus = [string][int]$Response.StatusCode
        } catch { $HttpStatus = "HTTP FAILED - inspect logs" }
        [pscustomobject]@{ App=$App.Name; Process=$(if ($Proc) { "RUNNING" } else { "EXITED" }); HTTP=$HttpStatus; PID=$App.PID; URL=$App.URL }
    }
    $Results | Format-Table -AutoSize
    if (@($Results | Where-Object { $_.Process -ne "RUNNING" -or $_.HTTP -ne "200" }).Count -gt 0) {
        throw "Een of meer apps zijn niet gestart of geven geen HTTP 200 terug. De start wordt teruggedraaid."
    }
    Write-Host "Logbestanden: $LogDir" -ForegroundColor DarkGray
    Write-Host "Alle apps binden aan 127.0.0.1; er worden geen firewall- of hostnetwerkwijzigingen uitgevoerd." -ForegroundColor Yellow
    Write-Host "Client : http://127.0.0.1:8510/"
    Write-Host "MGMT   : http://127.0.0.1:8511/"
    Write-Host "INFRA  : http://127.0.0.1:8512/"
} catch {
    foreach ($App in $Started) {
        Stop-Process -Id $App.PID -Force -ErrorAction SilentlyContinue
    }
    throw
}
