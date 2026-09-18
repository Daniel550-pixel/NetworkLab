param(
    [int]$Port = 3000,
    [switch]$NoBrowser,
    [switch]$SkipPull
)

$ErrorActionPreference = 'Stop'
$Root = $PSScriptRoot
$Url = "http://localhost:$Port"
$LogDir = Join-Path $Root 'logs'
$StdOutLog = Join-Path $LogDir 'networklab-web.out.log'
$StdErrLog = Join-Path $LogDir 'networklab-web.err.log'

if (-not (Test-Path (Join-Path $Root '.git'))) {
    throw "NetworkLab Git repository not found: $Root"
}

if (-not $SkipPull) {
    Write-Host "Updating NetworkLab from GitHub..." -ForegroundColor Cyan
    git -C $Root pull origin main
    if ($LASTEXITCODE -ne 0) {
        throw "git pull failed with exit code $LASTEXITCODE"
    }
}

$Server = Join-Path $Root 'Start-NetworkLabWeb.ps1'
$Index = Join-Path $Root 'web\index.html'

if (-not (Test-Path $Server)) { throw "Web server script not found: $Server" }
if (-not (Test-Path $Index)) { throw "Web UI not found: $Index" }

$existing = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
if ($existing) {
    Write-Host "Port $Port is already in use." -ForegroundColor Yellow
    Write-Host "Open: $Url" -ForegroundColor Green
    if (-not $NoBrowser) { Start-Process $Url }
    return
}

New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
Remove-Item $StdOutLog,$StdErrLog -Force -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "NETWORKLAB" -ForegroundColor Cyan
Write-Host "Repository: $Root" -ForegroundColor DarkGray
Write-Host "Starting local webapp..." -ForegroundColor Cyan

$argumentList = @('-NoProfile','-ExecutionPolicy','Bypass','-File',$Server,'-Port',$Port)

$serverProcess = Start-Process powershell.exe -ArgumentList $argumentList -RedirectStandardOutput $StdOutLog -RedirectStandardError $StdErrLog -PassThru

Start-Sleep -Seconds 2

if ($serverProcess.HasExited) {
    Write-Host ""
    Write-Host "Backend failed to start." -ForegroundColor Red
    Write-Host "STDOUT: $StdOutLog" -ForegroundColor Yellow
    Write-Host "STDERR: $StdErrLog" -ForegroundColor Yellow
    if (Test-Path $StdOutLog) { Get-Content $StdOutLog | Write-Host }
    if (Test-Path $StdErrLog) { Get-Content $StdErrLog | Write-Host }
    throw "NetworkLab web backend exited with code $($serverProcess.ExitCode)."
}

$listener = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
if (-not $listener) {
    Write-Host ""
    Write-Host "Backend process exists, but port $Port is not listening." -ForegroundColor Red
    Write-Host "STDOUT: $StdOutLog" -ForegroundColor Yellow
    Write-Host "STDERR: $StdErrLog" -ForegroundColor Yellow
    if (Test-Path $StdOutLog) { Get-Content $StdOutLog | Write-Host }
    if (Test-Path $StdErrLog) { Get-Content $StdErrLog | Write-Host }
    Stop-Process -Id $serverProcess.Id -Force -ErrorAction SilentlyContinue
    throw "NetworkLab backend did not bind to $Url."
}

Write-Host "Webapp running: $Url" -ForegroundColor Green
Write-Host "Backend PID: $($serverProcess.Id)" -ForegroundColor DarkGray
Write-Host "Logs: $LogDir" -ForegroundColor DarkGray

if (-not $NoBrowser) {
    Start-Process $Url
}

Write-Host "Press Ctrl+C to stop the launcher and backend." -ForegroundColor DarkGray

try {
    while (-not $serverProcess.HasExited) {
        Start-Sleep -Seconds 1
    }
}
finally {
    if (-not $serverProcess.HasExited) {
        Stop-Process -Id $serverProcess.Id -Force -ErrorAction SilentlyContinue
    }
}
