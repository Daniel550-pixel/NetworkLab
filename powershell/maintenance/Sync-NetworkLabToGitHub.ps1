#requires -Version 5.1
<#
.SYNOPSIS
  Synchroniseert veilige NetworkLab-wijzigingen naar GitHub.
.DESCRIPTION
  Werkt alleen op feature/three-webapps-no-vms. Geen force-push.
  Stopt als de Git-index al staged wijzigingen bevat, zodat niets onbedoeld wordt gecommit.
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
Write-Host '[1/6] Controleren of de Git-index schoon is' -ForegroundColor Cyan
$PreStaged = @(& git diff --cached --name-only)
if ($LASTEXITCODE -ne 0) { throw 'Git-index kon niet worden gecontroleerd.' }
if ($PreStaged.Count -gt 0) {
    Write-Host 'Deze bestanden stonden al staged vóór de synchronisatie:' -ForegroundColor Yellow
    $PreStaged | ForEach-Object { Write-Host "  $_" }
    throw 'Veiligheidsstop: commit niets automatisch. Controleer eerst bovenstaande staging.'
}
& git status --short
if ($LASTEXITCODE -ne 0) { throw 'git status is mislukt.' }

Write-Host ''
Write-Host '[2/6] GitHub ophalen en vergelijken' -ForegroundColor Cyan
Invoke-Git -GitArgs @('fetch','origin',$ExpectedBranch)
$Counts = (& git rev-list --left-right --count "HEAD...origin/$ExpectedBranch").Trim() -split '\s+'
if ($Counts.Count -lt 2) { throw 'Lokale en remote commits konden niet worden vergeleken.' }
if ([int]$Counts[1] -gt 0) {
    throw "GitHub loopt $($Counts[1]) commit(s) voor. Voer eerst uit: git pull --ff-only origin $ExpectedBranch"
}

Write-Host ''
Write-Host '[3/6] Kandidaten verzamelen' -ForegroundColor Cyan
$Untracked = @(& git ls-files --others --exclude-standard)
if ($LASTEXITCODE -ne 0) { throw 'Nieuwe bestanden konden niet worden opgesomd.' }
$Changed = @(& git diff --name-only)
if ($LASTEXITCODE -ne 0) { throw 'Gewijzigde bestanden konden niet worden opgesomd.' }
$Deleted = @(& git ls-files --deleted)
if ($LASTEXITCODE -ne 0) { throw 'Verwijderde bestanden konden niet worden opgesomd.' }
$Candidates = @(@($Untracked) + @($Changed) + @($Deleted) | Sort-Object -Unique)

$UnsafePattern = '(^|/)(evidence/runtime|logs)(/|$)|(^|/)Windows PowerShell(?: \d+)?\.txt$|\.bak(?:[-.]|$)|(^|/)\.env(?:\..*)?$|(^|/)(credentials\.json|id_rsa|id_ed25519)$|(^|/)(secrets|node_modules|\.venv|venv|__pycache__)(/|$)|(^|/).*\.log$'
$Safe = @($Candidates | Where-Object { $_ -and $_ -notmatch $UnsafePattern })
$Skipped = @($Candidates | Where-Object { $_ -and $_ -match $UnsafePattern })
if ($Skipped.Count -gt 0) {
    Write-Host 'Uitgesloten bestanden (blijven lokaal):' -ForegroundColor Yellow
    $Skipped | ForEach-Object { Write-Host "  $_" }
}

Write-Host ''
Write-Host '[4/6] Alleen veilige wijzigingen stagen' -ForegroundColor Cyan
foreach ($Path in $Safe) {
    Invoke-Git -GitArgs @('add','-A','--',$Path)
}
$Staged = @(& git diff --cached --name-only)
if ($LASTEXITCODE -ne 0) { throw 'Staged wijzigingen konden niet worden gecontroleerd.' }
$UnsafeStaged = @($Staged | Where-Object { $_ -match $UnsafePattern })
if ($UnsafeStaged.Count -gt 0) {
    & git restore --staged -- $UnsafeStaged
    throw 'Veiligheidsstop: onveilige bestanden zijn uit staging gehaald. Er is niets gecommit of gepusht.'
}
if ($Staged.Count -eq 0) {
    Write-Host 'Geen veilige lokale wijzigingen om te committen.' -ForegroundColor Yellow
} else {
    Write-Host 'Bestanden in de commit:' -ForegroundColor Cyan
    $Staged | ForEach-Object { Write-Host "  $_" }
    Write-Host ''
    Write-Host '[5/6] Commit maken' -ForegroundColor Cyan
    Invoke-Git -GitArgs @('commit','-m',$CommitMessage)
}

Write-Host ''
Write-Host '[6/6] Pushen en status controleren' -ForegroundColor Cyan
Invoke-Git -GitArgs @('push','origin',$ExpectedBranch)
Invoke-Git -GitArgs @('status','--short','--branch')
Write-Host 'Synchronisatie voltooid.' -ForegroundColor Green
