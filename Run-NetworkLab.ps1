param(
    [int]$Port = 8501,
    [switch]$NoBrowser
)

$ErrorActionPreference = 'Stop'
$Root = $PSScriptRoot
$Server = Join-Path $Root 'app\server.py'
$Url = "http://127.0.0.1:$Port"

if (-not (Test-Path (Join-Path $Root '.git'))) {
    throw "NetworkLab Git repository not found: $Root"
}

if (-not (Test-Path $Server)) {
    throw "Local web server not found: $Server"
}

$PythonCommand = Get-Command python.exe -ErrorAction SilentlyContinue
if (-not $PythonCommand) {
    throw "Python was not found on PATH."
}

$PythonPath = $PythonCommand.Source
if ([string]::IsNullOrWhiteSpace($PythonPath)) {
    $PythonPath = $PythonCommand.Path
}

$existing = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
if ($existing) {
    Write-Host "NetworkLab is already running: $Url" -ForegroundColor Green
    if (-not $NoBrowser) { Start-Process $Url }
    return
}

Write-Host ""
Write-Host "NETWORKLAB" -ForegroundColor Cyan
Write-Host "Mode: pure localhost web application" -ForegroundColor DarkGray
Write-Host "Server: $Server" -ForegroundColor DarkGray
Write-Host "URL: $Url" -ForegroundColor Green
Write-Host ""

$env:NETWORKLAB_PORT = "$Port"

$process = Start-Process `
    -FilePath $PythonPath `
    -ArgumentList "-m app.server" `
    -WorkingDirectory $Root `
    -PassThru `
    -WindowStyle Hidden

Start-Sleep -Seconds 2

$listener = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
if (-not $listener) {
    if ($process.HasExited) {
        throw "NetworkLab local server failed to start. Exit code: $($process.ExitCode)"
    }
    Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
    throw "NetworkLab did not open port $Port."
}

Write-Host "NetworkLab running: $Url" -ForegroundColor Green
Write-Host "Python PID: $($process.Id)" -ForegroundColor DarkGray

if (-not $NoBrowser) {
    Start-Process $Url
}

Write-Host "Local web app detached from this terminal." -ForegroundColor DarkGray
