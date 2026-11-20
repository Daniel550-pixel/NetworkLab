[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$LogDir = Join-Path $ProjectRoot "logs"
$LogFile = Join-Path $LogDir "networklab-autorecovery.log"
New-Item -ItemType Directory -Path $LogDir -Force | Out-Null

$PythonCommand = Get-Command python.exe -ErrorAction SilentlyContinue
if (-not $PythonCommand) { $PythonCommand = Get-Command python -ErrorAction SilentlyContinue }
if (-not $PythonCommand) {
    Add-Content -LiteralPath $LogFile -Encoding UTF8 -Value "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ERROR Python 3 niet gevonden in PATH."
    throw "Python 3 niet gevonden. Installeer Python 3 en voeg het toe aan PATH."
}
$Python = $PythonCommand.Source

function Write-NetworkLabLog([string]$Message) {
    Add-Content -LiteralPath $LogFile -Encoding UTF8 -Value "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') $Message"
}

$Apps = @(
    @{ Name="CLIENT"; Port=8510; Url="http://127.0.0.1:8510/"; Dir=(Join-Path $ProjectRoot "apps\client"); Kind="static" },
    @{ Name="MGMT"; Port=8511; Url="http://127.0.0.1:8511/"; Dir=(Join-Path $ProjectRoot "apps\mgmt"); Kind="static" },
    @{ Name="INFRA"; Port=8512; Url="http://127.0.0.1:8512/"; Dir=(Join-Path $ProjectRoot "apps\infra"); Kind="infra" }
)

foreach ($App in $Apps) {
    try {
        $Response = Invoke-WebRequest -Uri $App.Url -Method Get -UseBasicParsing -TimeoutSec 4
        if ([int]$Response.StatusCode -eq 200) {
            Write-NetworkLabLog "OK $($App.Name): HTTP 200"
            continue
        }
    } catch {}

    $Listener = Get-NetTCPConnection -State Listen -LocalPort $App.Port -ErrorAction SilentlyContinue
    if ($Listener) {
        Write-NetworkLabLog "WARNING $($App.Name): poort $($App.Port) bezet, maar URL reageert niet. Geen proces gestopt."
        continue
    }

    if (-not (Test-Path -LiteralPath $App.Dir -PathType Container)) {
        Write-NetworkLabLog "ERROR $($App.Name): applicatiemap ontbreekt: $($App.Dir)"
        continue
    }

    if ($App.Kind -eq "infra") {
        $Entry = Join-Path $App.Dir "server.py"
        if (-not (Test-Path -LiteralPath $Entry -PathType Leaf)) {
            Write-NetworkLabLog "ERROR INFRA: server.py ontbreekt."
            continue
        }
        $Arguments = @('"' + $Entry + '"')
    } else {
        $Arguments = @("-m", "http.server", [string]$App.Port, "--bind", "127.0.0.1", "--directory", ('"' + $App.Dir + '"'))
    }

    try {
        $OutLog = Join-Path $LogDir ("networklab-" + $App.Name.ToLowerInvariant() + ".out.log")
        $ErrLog = Join-Path $LogDir ("networklab-" + $App.Name.ToLowerInvariant() + ".err.log")
        Start-Process -FilePath $Python -ArgumentList $Arguments -WorkingDirectory $ProjectRoot -WindowStyle Hidden -RedirectStandardOutput $OutLog -RedirectStandardError $ErrLog | Out-Null

        Start-Sleep -Seconds 3
        try {
            $Response = Invoke-WebRequest -Uri $App.Url -UseBasicParsing -TimeoutSec 4
            if ([int]$Response.StatusCode -eq 200) {
                Write-NetworkLabLog "RECOVERED $($App.Name): HTTP 200"
            } else {
                Write-NetworkLabLog "ERROR $($App.Name): HTTP-status $([int]$Response.StatusCode)"
            }
        } catch {
            Write-NetworkLabLog "ERROR $($App.Name): gestart maar niet bereikbaar. Controleer $($App.Name.ToLowerInvariant())-err.log."
        }
    } catch {
        Write-NetworkLabLog "ERROR $($App.Name): $($_.Exception.Message)"
    }
}
