[CmdletBinding()]
param([string]$OutputDirectory)
$ErrorActionPreference = "Stop"
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$Timestamp = [DateTime]::UtcNow.ToString("yyyyMMdd-HHmmssZ")
if ([string]::IsNullOrWhiteSpace($OutputDirectory)) {
    $OutputDirectory = Join-Path $ProjectRoot "evidence\runtime\evidence-package-$Timestamp"
} elseif (-not [System.IO.Path]::IsPathRooted($OutputDirectory)) {
    $OutputDirectory = Join-Path $ProjectRoot $OutputDirectory
}
New-Item -ItemType Directory -Path $OutputDirectory -Force | Out-Null
$Checks = New-Object System.Collections.Generic.List[object]
function Add-Check {
    param([string]$Name,[string]$Result,[string]$Detail)
    $Checks.Add([pscustomobject]@{Name=$Name;Result=$Result;Detail=$Detail}) | Out-Null
}

# Capture only the listeners belonging to the three documented app ports.
$Listeners = foreach ($Port in @(8510,8511,8512)) {
    $Connections = @(Get-NetTCPConnection -State Listen -LocalPort $Port -ErrorAction SilentlyContinue)
    if ($Connections.Count -eq 0) {
        [pscustomobject]@{Port=$Port;Listening=$false;ProcessId=$null;ProcessName=$null}
        Add-Check "TCP listener $Port" "FAILED" "No listener found."
    } else {
        foreach ($Connection in $Connections) {
            $Process = Get-Process -Id $Connection.OwningProcess -ErrorAction SilentlyContinue
            [pscustomobject]@{Port=$Port;Listening=$true;ProcessId=$Connection.OwningProcess;ProcessName=$(if($Process){$Process.ProcessName}else{"Unknown"})}
        }
        Add-Check "TCP listener $Port" "OK" "Listener present."
    }
}

# Run the existing HTTP test in a child process because it uses exit codes.
$RuntimeReport = Join-Path $OutputDirectory "webapps-runtime.json"
$RuntimeScript = Join-Path $ProjectRoot "powershell\diagnostics\Test-NetworkLabWebApps.ps1"
$PowerShellExe = Join-Path $PSHOME "powershell.exe"
if (-not (Test-Path -LiteralPath $PowerShellExe)) {$PowerShellExe=(Get-Command powershell.exe -ErrorAction Stop).Source}
$RuntimeLog = Join-Path $OutputDirectory "webapps-runtime-console.txt"
$RuntimeErrorLog = Join-Path $OutputDirectory "webapps-runtime-error.txt"
$Arguments = "-NoProfile -ExecutionPolicy Bypass -File " + [char]34 + $RuntimeScript + [char]34 + " -OutputPath " + [char]34 + $RuntimeReport + [char]34
$RuntimeProcess = Start-Process -FilePath $PowerShellExe -ArgumentList $Arguments -Wait -PassThru -NoNewWindow -RedirectStandardOutput $RuntimeLog -RedirectStandardError $RuntimeErrorLog
if ($RuntimeProcess.ExitCode -eq 0 -and (Test-Path -LiteralPath $RuntimeReport)) {
    Add-Check "Five-point HTTP validation" "OK" "All five HTTP/API checks passed."
} else {
    Add-Check "Five-point HTTP validation" "FAILED" "Exit code $($RuntimeProcess.ExitCode); inspect webapps-runtime-console.txt."
}

# Run the Python unit tests and compile check.
$Python = Get-Command python -ErrorAction SilentlyContinue
if ($Python) {
    $UnitLog = Join-Path $OutputDirectory "python-unittest.txt"
    $UnitOutput = & $Python.Source -m unittest discover -s (Join-Path $ProjectRoot "tests") -p "test_*.py" -v 2>&1
    $UnitExit = $LASTEXITCODE
    $UnitOutput | Out-String | Set-Content -LiteralPath $UnitLog -Encoding UTF8
    Add-Check "Python unit tests" $(if($UnitExit -eq 0){"OK"}else{"FAILED"}) "Exit code $UnitExit; see python-unittest.txt."

    $CompileLog = Join-Path $OutputDirectory "python-compileall.txt"
    $CompileOutput = & $Python.Source -m compileall -q (Join-Path $ProjectRoot "apps") (Join-Path $ProjectRoot "tests") (Join-Path $ProjectRoot "python") 2>&1
    $CompileExit = $LASTEXITCODE
    $CompileOutput | Out-String | Set-Content -LiteralPath $CompileLog -Encoding UTF8
    Add-Check "Python compileall" $(if($CompileExit -eq 0){"OK"}else{"FAILED"}) "Exit code $CompileExit; see python-compileall.txt."
} else {
    Add-Check "Python unit tests" "BLOCKED" "Python command not found in PATH."
    Add-Check "Python compileall" "BLOCKED" "Python command not found in PATH."
}

# Capture Git metadata without changing the working tree.
$Git = Get-Command git -ErrorAction SilentlyContinue
$GitState = [ordered]@{Available=[bool]$Git;Branch=$null;Commit=$null;Status=$null}
if ($Git) {
    $GitState.Branch = (& $Git.Source -C $ProjectRoot branch --show-current 2>&1 | Out-String).Trim()
    $GitState.Commit = (& $Git.Source -C $ProjectRoot rev-parse HEAD 2>&1 | Out-String).Trim()
    $GitState.Status = (& $Git.Source -C $ProjectRoot status --short 2>&1 | Out-String).Trim()
}
$Passed = @($Checks | Where-Object {$_.Result -eq "OK"}).Count
$Failed = @($Checks | Where-Object {$_.Result -eq "FAILED"}).Count
$Blocked = @($Checks | Where-Object {$_.Result -eq "BLOCKED"}).Count
$Report = [ordered]@{
    Project="NetworkLab"
    GeneratedAtUtc=[DateTime]::UtcNow.ToString("o")
    Scope="Local Windows evidence collection; read-only."
    Summary=[ordered]@{Total=$Checks.Count;Passed=$Passed;Failed=$Failed;Blocked=$Blocked;Result=$(if($Failed -eq 0 -and $Blocked -eq 0){"PASS"}elseif($Passed -gt 0){"PARTIAL"}else{"FAIL"})}
    Git=$GitState
    Listeners=@($Listeners)
    Checks=@($Checks)
    EvidenceLimitations=@(
        "HTTP 200 proves reachability, not full internal functionality.",
        "This collector does not capture screenshots or prove GUI interaction.",
        "This collector does not perform failure-recovery or Windows reboot tests.",
        "Review screenshots and logs for passwords, tokens and personal data before sharing."
    )
}
$Report | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $OutputDirectory "evidence-summary.json") -Encoding UTF8

$Checklist = @"
# NetworkLab — manual evidence supplement

Package generated: $([DateTime]::UtcNow.ToString("yyyy-MM-dd HH:mm:ss 'UTC'"))

- [ ] Screenshot of Client UI at http://127.0.0.1:8510
- [ ] Screenshot of Management UI at http://127.0.0.1:8511
- [ ] Screenshot of Infrastructure UI at http://127.0.0.1:8512
- [ ] Screenshot of WiFi Profile Manager with NetworkLab-webapps button visible
- [ ] Screenshot of NetworkLab status window with all three statuses
- [ ] Screenshot of the five-point test showing 5/5 passing checks
- [ ] If required: controlled failure/recovery test with before/after report
- [ ] If autostart is claimed: Windows reboot test with date/time and post-login status
- [ ] Compare the dossier with the official school assessment criteria

Privacy: redact passwords, tokens, Wi-Fi keys and irrelevant personal data.
"@
$Checklist | Set-Content -LiteralPath (Join-Path $OutputDirectory "MANUAL-CAPTURE-CHECKLIST.md") -Encoding UTF8
$Manifest = Get-ChildItem -LiteralPath $OutputDirectory -File | Where-Object {$_.Name -ne "SHA256-MANIFEST.csv"} | ForEach-Object {
    [pscustomobject]@{File=$_.Name;SHA256=(Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash}
}
$Manifest | Export-Csv -LiteralPath (Join-Path $OutputDirectory "SHA256-MANIFEST.csv") -NoTypeInformation -Encoding UTF8
Write-Host ""
Write-Host "Evidence package: $OutputDirectory" -ForegroundColor Cyan
Write-Host "Passed: $Passed | Failed: $Failed | Blocked: $Blocked"
if ($Failed -gt 0 -or $Blocked -gt 0) {exit 1}
exit 0
