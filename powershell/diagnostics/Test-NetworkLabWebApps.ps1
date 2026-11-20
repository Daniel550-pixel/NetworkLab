[CmdletBinding()]
param(
    [Parameter()]
    [string]$OutputPath
)

$ErrorActionPreference = "Stop"
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$Timestamp = [DateTime]::UtcNow.ToString("yyyyMMdd-HHmmssZ")

$Checks = @(
    [pscustomobject]@{ Name = "Client UI"; Url = "http://127.0.0.1:8510/"; ExpectedApiStatus = $null },
    [pscustomobject]@{ Name = "Management UI"; Url = "http://127.0.0.1:8511/"; ExpectedApiStatus = $null },
    [pscustomobject]@{ Name = "Infrastructure UI"; Url = "http://127.0.0.1:8512/"; ExpectedApiStatus = $null },
    [pscustomobject]@{ Name = "Infrastructure health API"; Url = "http://127.0.0.1:8512/api/health"; ExpectedApiStatus = "ok" },
    [pscustomobject]@{ Name = "Infrastructure status API"; Url = "http://127.0.0.1:8512/api/status"; ExpectedApiStatus = "ok" }
)

$Results = foreach ($Check in $Checks) {
    $Watch = [System.Diagnostics.Stopwatch]::StartNew()
    try {
        $Response = Invoke-WebRequest -Uri $Check.Url -Method Get -UseBasicParsing -TimeoutSec 5
        $Detail = "HTTP response received"
        $Result = "FAILED"

        if ([int]$Response.StatusCode -eq 200) {
            $Result = "OK"
            if ($Check.ExpectedApiStatus) {
                $Payload = $Response.Content | ConvertFrom-Json
                if ($Payload.status -ne $Check.ExpectedApiStatus) {
                    $Result = "FAILED"
                    $Detail = "Expected API status '$($Check.ExpectedApiStatus)', received '$($Payload.status)'"
                } else {
                    $Detail = "HTTP 200; API status=$($Payload.status)"
                }
            } else {
                $Detail = "HTTP 200"
            }
        } else {
            $Detail = "Unexpected HTTP status $([int]$Response.StatusCode)"
        }

        [pscustomobject]@{
            Name = $Check.Name
            Url = $Check.Url
            HttpStatus = [int]$Response.StatusCode
            Result = $Result
            DurationMs = $Watch.ElapsedMilliseconds
            Detail = $Detail
        }
    } catch {
        $StatusCode = $null
        if ($_.Exception.Response -and $_.Exception.Response.StatusCode) {
            $StatusCode = [int]$_.Exception.Response.StatusCode
        }
        [pscustomobject]@{
            Name = $Check.Name
            Url = $Check.Url
            HttpStatus = $StatusCode
            Result = "FAILED"
            DurationMs = $Watch.ElapsedMilliseconds
            Detail = $_.Exception.Message
        }
    } finally {
        $Watch.Stop()
    }
}

$Passed = @($Results | Where-Object { $_.Result -eq "OK" }).Count
$Failed = @($Results | Where-Object { $_.Result -ne "OK" }).Count
$Report = [ordered]@{
    Project = "NetworkLab"
    GeneratedAtUtc = [DateTime]::UtcNow.ToString("o")
    Scope = "Local read-only HTTP reachability; no configuration changes"
    Summary = [ordered]@{
        Total = @($Results).Count
        Passed = $Passed
        Failed = $Failed
        Result = if ($Failed -eq 0) { "PASS" } else { "FAIL" }
    }
    Checks = @($Results)
}

if ([string]::IsNullOrWhiteSpace($OutputPath)) {
    $ReportDirectory = Join-Path $ProjectRoot "evidence\runtime"
    $OutputPath = Join-Path $ReportDirectory "networklab-webapps-$Timestamp.json"
} elseif (-not [System.IO.Path]::IsPathRooted($OutputPath)) {
    $OutputPath = Join-Path $ProjectRoot $OutputPath
}

$ReportDirectory = Split-Path -Parent $OutputPath
if (-not (Test-Path -LiteralPath $ReportDirectory -PathType Container)) {
    New-Item -ItemType Directory -Path $ReportDirectory -Force | Out-Null
}

$Report | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $OutputPath -Encoding UTF8
$Results | Select-Object Name, HttpStatus, Result, DurationMs, Detail | Format-Table -AutoSize
Write-Host ""
Write-Host "Runtime bewijs: $OutputPath"
Write-Host "Samenvatting: $Passed geslaagd; $Failed mislukt; totaal $(@($Results).Count)."

if ($Failed -gt 0) {
    exit 1
}
exit 0
