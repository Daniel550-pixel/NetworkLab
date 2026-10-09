# Installatiehandleiding NetworkLab

## 1. Vereisten

- Windows 11 of een compatibele Windows-versie.
- Git voor versiebeheer.
- Python 3 voor de lokale server, monitoring en rapportage.
- PowerShell voor beheerscripts.
- VirtualBox 7.x voor de VM-functies.
- Een browser voor de localhost-interface.

Controleer de beschikbare versies:

    git --version
    python --version
    $PSVersionTable.PSVersion

Optionele VirtualBox-controle:

    $VBoxManage = 'C:\Program Files\Oracle\VirtualBox\VBoxManage.exe'
    if (Test-Path $VBoxManage) { & $VBoxManage --version } else { Write-Warning 'VirtualBox niet gevonden.' }

## 2. Repository ophalen of bijwerken

Nieuwe installatie:

    git clone https://github.com/Daniel550-pixel/NetworkLab.git
    Set-Location .\NetworkLab

Bestaande lokale repository:

    Set-Location 'C:\Users\Daan Salden\Downloads\NetworkLab'
    git status --short --branch
    git pull

Controleer vóór synchronisatie op lokale wijzigingen. Commit of bewaar eigen werk voordat je bestanden bijwerkt.

## 3. Start de webapp

Gebruik de launcher die in de huidige repository staat:

    .\Run-NetworkLab.ps1

Als deze launcher ontbreekt, controleer eerst de actuele README en bestanden; gebruik niet blind een oud startcommando. De server-entrypoint is gedocumenteerd als app/server.py.

Open http://127.0.0.1:8501 in de browser. De applicatie is bedoeld voor lokaal gebruik; stel de server niet bloot aan een openbaar netwerk. Stop de server met Ctrl+C in de terminal waarin deze draait.

## 4. Controle na installatie

- De server start zonder traceback.
- De browser opent de interface op localhost.
- De belangrijkste pagina's laden zonder foutmelding.
- Lokale API-controles leveren een bruikbare respons.
- Veiligheidsinstellingen blijven standaard restrictief.
- Diagnostische scripts zijn uitvoerbaar vanuit de repositoryroot.

Registreer foutmeldingen letterlijk. Verwijder geen bestanden om een foutmelding te verbergen.

## 5. VirtualBox en gastbesturingssystemen

De VirtualBox-configuratie en gastbesturingssystemen vormen een aparte installatielaag. Volg [VM-installatiehandleiding](vm-installation-guide.md) en [VM-opslag](vm-storage.md). De Ubuntu Server ISO moet lokaal aanwezig zijn en de werkelijke VM-instellingen moeten vóór installatie worden gecontroleerd.

## 6. Problemen oplossen

| Probleem | Controle |
|---|---|
| Python niet gevonden | Controleer python --version en PATH |
| Poort 8501 bezet | Identificeer het proces; beëindig alleen een herkend proces |
| Launcher ontbreekt | Controleer repositoryroot en README |
| VBoxManage niet gevonden | Controleer het VirtualBox-installatiepad |
| Webapp laadt niet | Lees terminaluitvoer en controleer localhost/poort |
| Git pull weigert | Bekijk git status en bewaar lokale wijzigingen |

Zie ook [Troubleshooting](troubleshooting.md).
