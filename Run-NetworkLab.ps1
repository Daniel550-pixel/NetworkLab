param(
    [int]$Port = 3000,
    [switch]$NoBrowser,
    [switch]$SkipPull
)

$ErrorActionPreference = 'Stop'
$Root = $PSScriptRoot
$Url = "http://localhost:$Port"

if (-not (Test-Path (Join-Path $Root '.git'))) {
    throw "NetworkLab Git repository not found: $Root"
}

if (-not $SkipPull) {
    Write-Host "Updating NetworkLab from GitHub..." -ForegroundColor Cyan
    git -C $Root pull origin main
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

Write-Host ""
Write-Host "NETWORKLAB" -ForegroundColor Cyan
Write-Host "Repository: $Root" -ForegroundColor DarkGray
Write-Host "Starting local webapp..." -ForegroundColor Cyan

$serverProcess = Start-Process powershell.exe -ArgumentList @(
    '-NoProfile',
    '-ExecutionPolicy','Bypass',
    '-File',$Server,
    '-Port',$Port
) -PassThru

Start-Sleep -Milliseconds 800

if (-not $serverProcess.HasExited) {
    Write-Host "Webapp running: $Url" -ForegroundColor Green
    if (-not $NoBrowser) { Start-Process $Url }
    Write-Host "Backend PID: $($serverProcess.Id)" -ForegroundColor DarkGray
    Write-Host "Press Ctrl+C to stop the launcher and backend." -ForegroundColor DarkGray
    try {
        while (-not $serverProcess.HasExited) { Start-Sleep -Seconds 1 }
    }
    finally {
        if (-not $serverProcess.HasExited) { Stop-Process -Id $serverProcess.Id -Force -ErrorAction SilentlyContinue }
    }
}
else {
    throw "NetworkLab web backend exited immediately. Check the server output."
}
