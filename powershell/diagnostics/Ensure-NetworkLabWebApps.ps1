$ErrorActionPreference = "Stop"
$Root = "C:\Users\Daan Salden\Downloads\NetworkLab"
$LogDir = Join-Path $Root "logs"
$LogFile = Join-Path $LogDir "networklab-autorecovery.log"
$Python = "C:\Python314\python.exe"

function Log([string]$Message) {
    Add-Content -LiteralPath $LogFile -Encoding UTF8 -Value "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') $Message"
}

$Apps = @(
    @{ Name="CLIENT"; Port=8510; Url="http://127.0.0.1:8510/"; Dir=(Join-Path $Root "apps\client"); Kind="static" },
    @{ Name="MGMT"; Port=8511; Url="http://127.0.0.1:8511/"; Dir=(Join-Path $Root "apps\mgmt"); Kind="static" },
    @{ Name="INFRA"; Port=8512; Url="http://127.0.0.1:8512/"; Dir=(Join-Path $Root "apps\infra"); Kind="infra" }
)

foreach ($App in $Apps) {
    try {
        $Response = Invoke-WebRequest -Uri $App.Url -UseBasicParsing -TimeoutSec 4
        if ([int]$Response.StatusCode -eq 200) {
            Log "OK $($App.Name): HTTP 200"
            continue
        }
    } catch {}

    $Listener = Get-NetTCPConnection -State Listen -LocalPort $App.Port -ErrorAction SilentlyContinue
    if ($Listener) {
        Log "WARNING $($App.Name): poort $($App.Port) bezet, maar URL reageert niet. Geen proces gestopt."
        continue
    }

    if (-not (Test-Path $App.Dir -PathType Container)) {
        Log "ERROR $($App.Name): map ontbreekt: $($App.Dir)"
        continue
    }

    if ($App.Kind -eq "infra") {
        $Entry = Join-Path $App.Dir "server.py"
        if (-not (Test-Path $Entry -PathType Leaf)) {
            Log "ERROR INFRA: server.py ontbreekt."
            continue
        }
        $Arguments = "`"$Entry`""
    } else {
        $Arguments = "-m http.server $($App.Port) --bind 127.0.0.1 --directory `"$($App.Dir)`""
    }

    try {
        Start-Process -FilePath $Python -ArgumentList $Arguments `
            -WorkingDirectory $Root -WindowStyle Hidden `
            -RedirectStandardOutput (Join-Path $LogDir "networklab-$($App.Name.ToLower()).out.log") `
            -RedirectStandardError (Join-Path $LogDir "networklab-$($App.Name.ToLower()).err.log")

        Start-Sleep -Seconds 4
        try {
            $Response = Invoke-WebRequest -Uri $App.Url -UseBasicParsing -TimeoutSec 4
            if ([int]$Response.StatusCode -eq 200) {
                Log "RECOVERED $($App.Name): HTTP 200"
            } else {
                Log "ERROR $($App.Name): HTTP-status $($Response.StatusCode)"
            }
        } catch {
            Log "ERROR $($App.Name): gestart maar niet bereikbaar. Controleer de err-log."
        }
    } catch {
        Log "ERROR $($App.Name): $($_.Exception.Message)"
    }
}
