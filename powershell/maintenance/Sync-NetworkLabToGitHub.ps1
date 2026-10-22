#requires -Version 5.1
<#
.SYNOPSIS
  Controleert, commit en pusht veilige wijzigingen van NetworkLab naar GitHub.
.DESCRIPTION
  Werkt uitsluitend op feature/three-webapps-no-vms. Gebruikt geen force-push.
  Runtime-bewijs, logs, geheimen en tijdelijke PowerShell-captures blijven lokaal.
#>
[CmdletBinding()]
param([string]$CommitMessage = 'chore: sync NetworkLab workspace')
$ErrorActionPreference = 'Stop'
$ExpectedBranch = 'feature/three-webapps-no-vms'

function Invoke-Git {
    param([Parameter(Mandatory)][string[]]$GitArgs)
    & git @GitArgs
    if ($LASTEXITCODE -ne 0) {
        throw "Git-opdracht mislukt (exit $LASTEXITCODE): git $($GitArgs -join ' ')"
    }
}

$Root = (& git rev-parse --show-toplevel 2>$null)
if ($LASTEXITCODE -ne 0 -or -not $Root) { throw 'Open PowerShell in de lokale NetworkLab Git-map.' }
Set-Location $Root
$Branch = (& git branch --show-current).Trim()
if ($Branch -ne $ExpectedBranch) { throw "Verkeerde branch '$Branch'; verwacht '$ExpectedBranch'. Er is niets gepusht." }
$RemoteUrl = (& git remote get-url origin 2>$null)
if ($LASTEXITCODE -ne 0 -or $RemoteUrl -notmatch 'github\.com[:/]Daniel550-pixel/NetworkLab(?:\.git)?$') {
    throw 'origin verwijst niet naar Daniel550-pixel/NetworkLab.'
}

Write-Host ''
Write-Host '[1/5] Lokale wijzigingen controleren' -ForegroundColor Cyan
& git status --short
if ($LASTEXITCODE -ne 0) { throw 'git status is mislukt.' }

# Terminalcaptures, back-ups en mogelijke geheimen worden niet automatisch meegestuurd.
$Status = @(& git status --porcelain)
$Review = @($Status | Where-Object {
    $_ -match 'Windows PowerShell.*\.txt' -or
    $_ -match '\.bak([.-]|$)' -or
    $_ -match '(^|/)(\.env(\..*)?|credentials\.json|id_rsa|id_ed25519)(/|$)' -or
    $_ -match '(^|/)(secrets|node_modules|\.venv|venv|__pycache__)(/|$)'
})
if ($Review.Count -gt 0) {
    Write-Host 'Niet automatisch gepushte bestanden (eerst controleren):' -ForegroundColor Yellow
    $Review | ForEach-Object { Write-Host "  $_" }
}

Write-Host ''
Write-Host '[2/5] GitHub-status ophalen' -ForegroundColor Cyan
Invoke-Git -GitArgs @('fetch','origin',$ExpectedBranch)
$Counts = (& git rev-list --left-right --count "HEAD...origin/$ExpectedBranch").Trim() -split '\s+'
if ($Counts.Count -lt 2) { throw 'Lokale en remote commits konden niet worden vergeleken.' }
if ([int]$Counts[1] -gt 0) {
    throw "GitHub loopt $($Counts[1]) commit(s) voor. Synchroniseer eerst met git pull --rebase origin $ExpectedBranch."
}

Write-Host ''
Write-Host '[3/5] Veilige wijzigingen klaarzetten' -ForegroundColor Cyan
$CandidateFiles = @(& git ls-files --others --exclude-standard)
if ($LASTEXITCODE -ne 0) { throw 'Nieuwe bestanden konden niet worden opgesomd.' }
$TrackedChanged = @(& git diff --name-only)
if ($LASTEXITCODE -ne 0) { throw 'Gewijzigde bestanden konden niet worden opgesomd.' }
$TrackedDeleted = @(& git ls-files --deleted)
if ($LASTEXITCODE -ne 0) { throw 'Verwijderde bestanden konden niet worden opgesomd.' }
$AllCandidates = @($CandidateFiles) + @($TrackedChanged) + @($TrackedDeleted)
$SafeCandidates = @($AllCandidates | Sort-Object -Unique | Where-Object {
    $_ -and
    $_ -notmatch '(^|/)evidence/runtime(/|$)' -and
    $_ -notmatch '(^|/)logs/.*\.log$' -and
    $_ -notmatch '(^|/)Windows PowerShell.*\.txt$' -and
    $_ -notmatch '\.bak([.-]|$)' -and
    $_ -notmatch '(^|/)\.env(\..*)?$' -and
    $_ -notmatch '(^|/)(credentials\.json|id_rsa|id_ed25519)$' -and
    $_ -notmatch '(^|/)(secrets|node_modules|\.venv|venv|__pycache__)(/|$)'
})
foreach ($Path in $SafeCandidates) {
    Invoke-Git -GitArgs @('add','-A','--',$Path)
}
$Staged = @(& git diff --cached --name-only)
if ($LASTEXITCODE -ne 0) { throw 'Staged wijzigingen konden niet worden gecontroleerd.' }
if ($Staged.Count -eq 0) {
    Write-Host 'Geen veilige lokale wijzigingen om te committen.' -ForegroundColor Yellow
} else {
    Write-Host 'Bestanden in de commit:' -ForegroundColor Cyan
    $Staged | ForEach-Object { Write-Host "  $_" }
    Invoke-Git -GitArgs @('commit','-m',$CommitMessage)
}
Write-Host ''
Write-Host '[5/5] Naar GitHub pushen' -ForegroundColor Cyan
Invoke-Git -GitArgs @('push','origin',$ExpectedBranch)
Write-Host 'Synchronisatie voltooid.' -ForegroundColor Green
Invoke-Git -GitArgs @('status','--short','--branch')
