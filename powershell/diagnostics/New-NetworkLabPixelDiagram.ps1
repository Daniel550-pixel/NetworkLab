#requires -Version 5.1
<#
.SYNOPSIS
  Genereert een pixel-gepositioneerde PNG-netwerktekening voor NetworkLab.
.DESCRIPTION
  Tekent de architectuur met System.Drawing op een canvas van 1600 x 1050 pixels.
  Slaat de PNG op in evidence en kan deze optioneel openen.
#>
[CmdletBinding()]
param(
    [string]$OutputPath = (Join-Path (Split-Path $PSScriptRoot -Parent | Split-Path -Parent | Split-Path -Parent) 'evidence\networklab-netwerkdiagram.png'),
    [switch]$Open
)

$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing

$OutputDirectory = Split-Path -Parent $OutputPath
New-Item -ItemType Directory -Path $OutputDirectory -Force | Out-Null

$Width = 1600
$Height = 1050
$Bitmap = New-Object System.Drawing.Bitmap($Width, $Height)
$Graphics = [System.Drawing.Graphics]::FromImage($Bitmap)
$Graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::None
$Graphics.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::ClearTypeGridFit
$Graphics.Clear([System.Drawing.Color]::FromArgb(248, 250, 252))

$Ink = [System.Drawing.Color]::FromArgb(23, 43, 77)
$Muted = [System.Drawing.Color]::FromArgb(82, 100, 123)
$Blue = [System.Drawing.Color]::FromArgb(219, 234, 254)
$BlueLine = [System.Drawing.Color]::FromArgb(37, 99, 235)
$Green = [System.Drawing.Color]::FromArgb(220, 252, 231)
$GreenLine = [System.Drawing.Color]::FromArgb(21, 128, 61)
$White = [System.Drawing.Color]::White
$Grid = [System.Drawing.Color]::FromArgb(231, 237, 244)
$Amber = [System.Drawing.Color]::FromArgb(180, 83, 9)
$Font = New-Object System.Drawing.Font('Segoe UI', 16, [System.Drawing.FontStyle]::Regular)
$Bold = New-Object System.Drawing.Font('Segoe UI', 19, [System.Drawing.FontStyle]::Bold)
$Small = New-Object System.Drawing.Font('Segoe UI', 13, [System.Drawing.FontStyle]::Regular)
$HeaderFont = New-Object System.Drawing.Font('Segoe UI', 28, [System.Drawing.FontStyle]::Bold)
$BrushInk = New-Object System.Drawing.SolidBrush($Ink)
$BrushMuted = New-Object System.Drawing.SolidBrush($Muted)
$BrushWhite = New-Object System.Drawing.SolidBrush($White)
$BrushBlue = New-Object System.Drawing.SolidBrush($Blue)
$BrushGreen = New-Object System.Drawing.SolidBrush($Green)
$PenBlue = New-Object System.Drawing.Pen($BlueLine, 3)
$PenGreen = New-Object System.Drawing.Pen($GreenLine, 3)
$PenGray = New-Object System.Drawing.Pen([System.Drawing.Color]::FromArgb(100, 116, 139), 4)
$PenAmber = New-Object System.Drawing.Pen($Amber, 4)
$PenAmber.DashPattern = [single[]]@(3, 3)
$PenBlue.EndCap = [System.Drawing.Drawing2D.LineCap]::ArrowAnchor
$PenGreen.EndCap = [System.Drawing.Drawing2D.LineCap]::ArrowAnchor
$PenGray.EndCap = [System.Drawing.Drawing2D.LineCap]::ArrowAnchor
$PenAmber.EndCap = [System.Drawing.Drawing2D.LineCap]::ArrowAnchor

function Draw-Text {
    param([string]$Text, [int]$X, [int]$Y, [System.Drawing.Font]$UseFont = $Font, [System.Drawing.Brush]$Brush = $BrushInk)
    $Graphics.DrawString($Text, $UseFont, $Brush, [single]$X, [single]$Y)
}
function Draw-Node {
    param(
        [int]$X,[int]$Y,[int]$W,[int]$H,
        [string]$Title,[string]$Line1,[string]$Line2,
        [System.Drawing.Brush]$Fill,[System.Drawing.Pen]$Border
    )
    $Graphics.FillRectangle($Fill, $X, $Y, $W, $H)
    $Graphics.DrawRectangle($Border, $X, $Y, $W, $H)
    $TitleSize = [Math]::Max(12, [Math]::Min(18, [int](18 * 200 / [Math]::Max(200, $W))))
    $NodeTitleFont = New-Object System.Drawing.Font('Segoe UI', $TitleSize, [System.Drawing.FontStyle]::Bold)
    $TitleSizeMeasure = $Graphics.MeasureString($Title, $NodeTitleFont)
    $Graphics.DrawString($Title, $NodeTitleFont, $BrushInk, [single]($X + ($W - $TitleSizeMeasure.Width) / 2), [single]($Y + 13))
    $L1Measure = $Graphics.MeasureString($Line1, $Small)
    $Graphics.DrawString($Line1, $Small, $BrushInk, [single]($X + ($W - $L1Measure.Width) / 2), [single]($Y + 43))
    $L2Measure = $Graphics.MeasureString($Line2, $Small)
    $Graphics.DrawString($Line2, $Small, $BrushInk, [single]($X + ($W - $L2Measure.Width) / 2), [single]($Y + 66))
    $NodeTitleFont.Dispose()
}
function Draw-Section {
    param([int]$X,[int]$Y,[int]$W,[int]$H,[string]$Title,[System.Drawing.Pen]$Border)
    $Graphics.FillRectangle($BrushWhite, $X, $Y, $W, $H)
    $Graphics.DrawRectangle($Border, $X, $Y, $W, $H)
    Draw-Text $Title ($X + 20) ($Y + 12) $Bold $BrushInk
}
try {
    # Pixelgrid op vaste intervallen
    for ($X = 0; $X -lt $Width; $X += 20) {
        $Graphics.DrawLine((New-Object System.Drawing.Pen($Grid, 1)), $X, 0, $X, $Height)
    }
    for ($Y = 0; $Y -lt $Height; $Y += 20) {
        $Graphics.DrawLine((New-Object System.Drawing.Pen($Grid, 1)), 0, $Y, $Width, $Y)
    }

    $Graphics.FillRectangle((New-Object System.Drawing.SolidBrush($Ink)), 40, 28, 1520, 92)
    $Graphics.DrawRectangle((New-Object System.Drawing.Pen([System.Drawing.Color]::FromArgb(15, 31, 56), 3)), 40, 28, 1520, 92)
    Draw-Text 'NETWORKLAB' 72 43 $HeaderFont $BrushWhite
    Draw-Text 'Lokale architectuur | Windows PowerShell | runtime-bewijs' 72 82 $Small (New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(219, 234, 254)))

    Draw-Section 55 150 1490 145 'GEBRUIKER EN WINDOWS-HOST' $PenGray
    Draw-Node 82 199 270 68 'Gebruiker / browser' 'Lokale webinterface' 'HTTP naar localhost' $BrushBlue $PenBlue
    $Graphics.DrawLine($PenGray, 352, 233, 410, 233)
    Draw-Node 420 199 1060 68 'Windows-laptop | NetworkLab' 'Alle services binden aan 127.0.0.1' 'Niet publiek op het LAN aangeboden' $BrushBlue $PenBlue

    Draw-Section 55 320 720 390 'WEBAPPS EN API-SERVICES' $PenGreen
    Draw-Node 80 382 200 100 'Client UI' 'Poort 8510' 'HTTP 200 getest' $BrushGreen $PenGreen
    Draw-Node 310 382 200 100 'Management UI' 'Poort 8511' 'HTTP 200 getest' $BrushGreen $PenGreen
    Draw-Node 540 382 205 100 'Infrastructure UI' 'Poort 8512' 'HTTP 200 getest' $BrushGreen $PenGreen
    $Graphics.DrawLine($PenGreen, 642, 482, 642, 520)
    Draw-Node 100 535 285 95 'Health API' 'GET /api/health' 'HTTP 200' $BrushGreen $PenGreen
    Draw-Node 405 535 340 95 'Status API' 'GET /api/status' 'HTTP 200' $BrushGreen $PenGreen
    Draw-Text 'Client en MGMT kunnen INFRA via HTTP om status vragen.' 80 666 $Small $BrushMuted

    Draw-Section 805 320 740 390 'AUTOMATISCHE BESCHIKBAARHEID' $PenBlue
    Draw-Node 830 382 300 95 'Windows Taakplanner' 'Bij aanmelden + elke minuut' 'NetworkLab AutoRecovery' $BrushBlue $PenBlue
    $Graphics.DrawLine($PenGray, 1130, 430, 1170, 430)
    Draw-Node 1180 382 330 95 'Watchdog' 'Watch-NetworkLabAutoRecovery.ps1' 'Start supervisor indien afwezig' $BrushBlue $PenBlue
    $Graphics.DrawLine($PenGray, 1345, 477, 1345, 510)
    $Graphics.DrawLine($PenGray, 1345, 510, 980, 510)
    $Graphics.DrawLine($PenGray, 980, 510, 980, 540)
    Draw-Node 830 540 300 100 'Supervisor' 'Run-NetworkLabAutoRecovery.ps1' 'Herstelcyclus: 60 seconden' $BrushBlue $PenBlue
    $Graphics.DrawLine($PenGray, 1130, 590, 1170, 590)
    Draw-Node 1180 540 330 100 'Herstelworker' 'Ensure-NetworkLabWebApps.ps1' 'Controleert en herstelt services' $BrushBlue $PenBlue
    $Graphics.DrawLine($PenAmber, 1345, 640, 1345, 685)
    $Graphics.DrawLine($PenAmber, 1345, 685, 415, 685)
    $Graphics.DrawLine($PenAmber, 415, 685, 415, 711)
    Draw-Text 'Controle-/herstelpad naar de webapps' 790 657 $Small (New-Object System.Drawing.SolidBrush($Amber))

    Draw-Section 55 750 1490 250 'TESTBEWIJS | LAATSTE GERAPPORTEERDE RUN' $PenGray
    $Graphics.FillRectangle($BrushGreen, 85, 818, 250, 115)
    $Graphics.DrawRectangle($PenGreen, 85, 818, 250, 115)
    Draw-Text '5 / 5' 155 833 $HeaderFont (New-Object System.Drawing.SolidBrush($GreenLine))
    Draw-Text 'Geslaagd | 0 mislukt' 115 888 $Small (New-Object System.Drawing.SolidBrush($GreenLine))
    Draw-Text 'Runtime-rapport (lokaal)' 375 825 $Bold $BrushInk
    Draw-Text 'evidence/runtime/networklab-webapps-20261022-090657Z.json' 375 861 $Small $BrushInk
    Draw-Text 'Bewakingslog' 375 895 $Bold $BrushInk
    Draw-Text 'logs/networklab-autorecovery.log' 375 931 $Small $BrushInk
    Draw-Text 'Rapport gebaseerd op de aangeleverde PowerShell-testuitvoer; de tekening voert zelf geen tests uit.' 82 971 $Small $BrushMuted

    $Bitmap.Save($OutputPath, [System.Drawing.Imaging.ImageFormat]::Png)
    Write-Host "Netwerktekening opgeslagen: $OutputPath" -ForegroundColor Green
    Write-Host "Canvas: $Width x $Height pixels" -ForegroundColor Cyan
    if ($Open) { Start-Process -FilePath $OutputPath }
}
finally {
    $Graphics.Dispose()
    $Bitmap.Dispose()
    foreach ($Item in @($Font,$Bold,$Small,$HeaderFont,$BrushInk,$BrushMuted,$BrushWhite,$BrushBlue,$BrushGreen,$PenBlue,$PenGreen,$PenGray,$PenAmber)) {
        if ($null -ne $Item) { $Item.Dispose() }
    }
}
