#requires -Version 5.1
<# Safe Git sync for the NetworkLab workspace. No force-push; runtime evidence stays local. #>
[CmdletBinding()]
param([string]$CommitMessage = 'chore: sync NetworkLab workspace')
$ErrorActionPreference = 'Stop'
$ExpectedBranch = 'feature/three-webapps-no-vms'
function Invoke-Git { param([string[]]$GitArgs) & git @GitArgs; if ($LASTEXITCODE -ne 0) { throw "Git failed: $($GitArgs -join ' ')" } }
$Root = (& git rev-parse --show-toplevel 2>$null)
if ($LASTEXITCODE -ne 0 -or -not $Root) { throw 'Open PowerShell inside the NetworkLab Git repository.' }
Set-Location $Root
$Branch = (& git branch --show-current).Trim()
if ($Branch -ne $ExpectedBranch) { throw "Wrong branch '$Branch'; expected '$ExpectedBranch'. Nothing was pushed." }
$RemoteUrl = (& git remote get-url origin 2>$null)
if ($LASTEXITCODE -ne 0 -or $RemoteUrl -notmatch 'github\.com[:/]Daniel550-pixel/NetworkLab(?:\.git)?$') { throw 'origin is not the expected NetworkLab GitHub repository.' }
Write-Host 'Checking local changes...' -ForegroundColor Cyan
& git status --short
if ($LASTEXITCODE -ne 0) { throw 'git status failed.' }
$Blocked = @(& git status --porcelain | Where-Object { $_ -match '(^|/)(\.env|id_rsa|id_ed25519|credentials\.json|secrets?)(/|$)' -or $_ -match '(^|/)(node_modules|\.venv|venv|__pycache__)(/|$)' })
if ($Blocked.Count -gt 0) { $Blocked | ForEach-Object { Write-Host $_ -ForegroundColor Red }; throw 'Potential secret/cache paths found; nothing was committed.' }
Write-Host 'Fetching GitHub...' -ForegroundColor Cyan
Invoke-Git -GitArgs @('fetch','origin',$ExpectedBranch)
$Counts = (& git rev-list --left-right --count "HEAD...origin/$ExpectedBranch").Trim() -split '\s+'
if ($Counts.Count -lt 2) { throw 'Could not compare local and remote commits.' }
if ([int]$Counts[1] -gt 0) { throw "Remote branch is ahead by $($Counts[1]) commit(s). Run git pull --rebase origin $ExpectedBranch, then retry." }
Write-Host 'Staging changes (runtime JSON, logs, secrets and caches excluded)...' -ForegroundColor Cyan
Invoke-Git -GitArgs @('add','-A','--','.',' :(exclude)evidence/runtime/**'.Trim(),' :(exclude)logs/*.log'.Trim(),' :(exclude)**/.env'.Trim(),' :(exclude)**/.env.*'.Trim(),' :(exclude)**/secrets/**'.Trim(),' :(exclude)**/credentials.json'.Trim(),' :(exclude)**/id_rsa'.Trim(),' :(exclude)**/id_ed25519'.Trim(),' :(exclude)**/__pycache__/**'.Trim(),' :(exclude)**/node_modules/**'.Trim(),' :(exclude)**/.venv/**'.Trim(),' :(exclude)**/venv/**'.Trim())
$Staged = @(& git diff --cached --name-only)
if ($LASTEXITCODE -ne 0) { throw 'Could not inspect staged changes.' }
if ($Staged.Count -gt 0) { $Staged | ForEach-Object { Write-Host "  $_" }; Invoke-Git -GitArgs @('commit','-m',$CommitMessage) } else { Write-Host 'No local changes to commit.' -ForegroundColor Yellow }
Write-Host 'Pushing to GitHub...' -ForegroundColor Cyan
Invoke-Git -GitArgs @('push','origin',$ExpectedBranch)
Write-Host 'Sync complete.' -ForegroundColor Green
Invoke-Git -GitArgs @('status','--short','--branch')
