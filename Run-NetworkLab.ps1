param(
    [int]$Port = 8501,
    [switch]$NoBrowser,
    [switch]$SkipInstall
)

$ErrorActionPreference = 'Stop'
$Root = $PSScriptRoot
$App = Join-Path $Root 'app\main.py'
$Requirements = Join-Path $Root 'requirements.txt'
$Url = "http://localhost:$Port"

if (-not (Test-Path (Join-Path $Root '.git'))) {
    throw "NetworkLab Git repository not found: $Root"
}

if (-not (Test-Path $App)) {
    throw "Streamlit application not found: $App"
}

if (-not (Get-Command python.exe -ErrorAction SilentlyContinue)) {
    throw "Python was not found on PATH."
}

if (-not $SkipInstall) {
    Write-Host "Checking Streamlit dependency..." -ForegroundColor Cyan
    & python.exe -m pip install -r $Requirements
    if ($LASTEXITCODE -ne 0) {
        throw "Dependency installation failed."
    }
}

$existing = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue

if ($existing) {
    Write-Host "Port $Port is already in use." -ForegroundColor Yellow
    Write-Host "Opening $Url" -ForegroundColor Green
    if (-not $NoBrowser) { Start-Process $Url }
    return
}

Write-Host ""
Write-Host "NETWORKLAB" -ForegroundColor Cyan
Write-Host "Application: $App" -ForegroundColor DarkGray
Write-Host "Starting Streamlit..." -ForegroundColor Cyan
Write-Host ""

$LogDirectory = Join-Path $Root '.networklab'
$StdOutLog = Join-Path $LogDirectory 'streamlit.stdout.log'
$StdErrLog = Join-Path $LogDirectory 'streamlit.stderr.log'

New-Item -ItemType Directory -Path $LogDirectory -Force | Out-Null
Remove-Item $StdOutLog, $StdErrLog -Force -ErrorAction SilentlyContinue

# Windows PowerShell 5.1 can mishandle argument arrays when paths contain spaces.
# Pass the complete command line as one quoted argument string.
$arguments = "-m streamlit run `"$App` --server.port $Port --server.address 127.0.0.1 --browser.gatherUsageStats false"

$process = Start-Process ``
    -FilePath 'python.exe' ``
    -ArgumentList $arguments ``
    -WorkingDirectory $Root ``
    -RedirectStandardOutput $StdOutLog ``
    -RedirectStandardError $StdErrLog ``
    -PassThru

Start-Sleep -Seconds 4

$listener = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue

if (-not $listener) {
    $stderr = if (Test-Path $StdErrLog) { Get-Content $StdErrLog -Raw } else { '' }
    $stdout = if (Test-Path $StdOutLog) { Get-Content $StdOutLog -Raw } else { '' }

    if ($process.HasExited) {
        Write-Host ''
        Write-Host 'STREAMLIT STARTUP FAILED' -ForegroundColor Red
        Write-Host "Exit code: $($process.ExitCode)" -ForegroundColor Red
        if ($stderr.Trim()) {
            Write-Host ''
            Write-Host 'Error output:' -ForegroundColor Yellow
            Write-Host $stderr.Trim()
        }
        if ($stdout.Trim()) {
            Write-Host ''
            Write-Host 'Standard output:' -ForegroundColor Yellow
            Write-Host $stdout.Trim()
        }
        throw "Streamlit failed to start. Logs: $LogDirectory"
    }

    Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
    throw "Streamlit started but did not open port $Port. Logs: $LogDirectory"
}
Write-Host "NetworkLab running: $Url" -ForegroundColor Green
Write-Host "Streamlit PID: $($process.Id)" -ForegroundColor DarkGray
Write-Host "Press Ctrl+C to stop." -ForegroundColor DarkGray

if (-not $NoBrowser) {
    Start-Process $Url
}

try {
    while (-not $process.HasExited) {
        Start-Sleep -Seconds 1
    }
}
finally {
    if (-not $process.HasExited) {
        Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
    }
}
