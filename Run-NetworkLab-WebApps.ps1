[CmdletBinding()]
param([int]$ClientPort=8510,[int]$MgmtPort=8511,[int]$InfraPort=8512)
$ErrorActionPreference="Stop"
$ProjectRoot=Split-Path -Parent $MyInvocation.MyCommand.Path
$PythonCommand=Get-Command python -ErrorAction SilentlyContinue
if(-not $PythonCommand){throw "Python 3 is vereist. Installeer Python en controleer dat python in PATH staat."}
$Python=$PythonCommand.Source
$LogDir=Join-Path $ProjectRoot "logs"
New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
$Apps=@(
 @{Name="CLIENT";Port=$ClientPort;Url="http://127.0.0.1:$ClientPort";Directory=(Join-Path $ProjectRoot "apps\client");Kind="static"},
 @{Name="MGMT";Port=$MgmtPort;Url="http://127.0.0.1:$MgmtPort";Directory=(Join-Path $ProjectRoot "apps\mgmt");Kind="static"},
 @{Name="INFRA";Port=$InfraPort;Url="http://127.0.0.1:$InfraPort";Directory=(Join-Path $ProjectRoot "apps\infra");Kind="infra"}
)
foreach($App in $Apps){
 if(-not(Test-Path -LiteralPath $App.Directory -PathType Container)){throw "Applicatiemap ontbreekt: $($App.Directory)"}
 $Listener=Get-NetTCPConnection -State Listen -LocalPort $App.Port -ErrorAction SilentlyContinue
 if($Listener){throw "Poort $($App.Port) is al in gebruik. Er is niets gestart; controleer de listener voordat je opnieuw probeert."}
}
$Started=@()
foreach($App in $Apps){
 $OutLog=Join-Path $LogDir ("networklab-"+$App.Name.ToLowerInvariant()+".out.log")
 $ErrLog=Join-Path $LogDir ("networklab-"+$App.Name.ToLowerInvariant()+".err.log")
 if($App.Kind -eq "infra"){$Arguments=@(('"' + (Join-Path $App.Directory "server.py") + '"'))}
 else{$Arguments=@("-m","http.server",[string]$App.Port,"--bind","127.0.0.1","--directory",('"' + $App.Directory + '"'))}
 $Process=Start-Process -FilePath $Python -ArgumentList $Arguments -WorkingDirectory $ProjectRoot -WindowStyle Hidden -RedirectStandardOutput $OutLog -RedirectStandardError $ErrLog -PassThru
 $Started += [pscustomobject]@{Name=$App.Name;PID=$Process.Id;Port=$App.Port;URL=$App.Url}
}
Start-Sleep -Seconds 2
Write-Host "`n=== NETWORKLAB WEBAPPS ===" -ForegroundColor Cyan
foreach($App in $Started){$Proc=Get-Process -Id $App.PID -ErrorAction SilentlyContinue;$Status=if($Proc){"PROCESS STARTED"}else{"PROCESS EXITED - inspect logs"};[pscustomobject]@{App=$App.Name;Status=$Status;PID=$App.PID;URL=$App.Url}|Format-Table -AutoSize}
Write-Host "Logbestanden: $LogDir" -ForegroundColor DarkGray
Write-Host "Alle apps binden aan 127.0.0.1; er worden geen firewall- of hostnetwerkwijzigingen uitgevoerd." -ForegroundColor Yellow
