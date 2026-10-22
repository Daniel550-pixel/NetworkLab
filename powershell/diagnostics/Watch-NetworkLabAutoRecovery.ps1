$ErrorActionPreference = 'SilentlyContinue'
$Root = Join-Path $HOME 'Downloads\NetworkLab'
$Supervisor = Join-Path $Root 'powershell\diagnostics\Run-NetworkLabAutoRecovery.ps1'
$Log = Join-Path $Root 'logs\networklab-autorecovery.log'
$PSExe = "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe"

if (-not (Test-Path -LiteralPath $Supervisor)) { exit 2 }

$Running = Get-CimInstance Win32_Process |
    Where-Object {
        $_.Name -ieq 'powershell.exe' -and
        $_.CommandLine -match 'Run-NetworkLabAutoRecovery\.ps1'
    }

if (-not $Running) {
    Start-Process -FilePath $PSExe `
        -ArgumentList "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$Supervisor`"" `
        -WorkingDirectory $Root `
        -WindowStyle Hidden

    Add-Content -LiteralPath $Log -Encoding UTF8 `
        -Value "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') WATCHDOG: supervisor gestart"
}
