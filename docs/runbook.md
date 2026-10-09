# NetworkLab Runbook

## Doel en veilige volgorde

Dit runbook is de korte operationele checklist. Begin met read-only controles en voer geen netwerkconfiguratie uit wanneer de lab-scope niet duidelijk is. Controleer in de huidige checkout of een genoemd script bestaat voordat je het uitvoert.

## 1. Repository en omgeving

    git status --short --branch
    python --version
    $PSVersionTable.PSVersion

Bekijk eerst de lokale wijzigingen. Bewaar eigen werk voordat je de repository synchroniseert.

## 2. Initialiseren en inspecteren

    ./powershell/install/Initialize-NetworkLab.ps1
    ./powershell/configure/Get-NetworkLabState.ps1
    ./powershell/configure/Get-NetworkConfiguration.ps1

De initialisatie hoort vereisten te controleren; inspectiescripts verzamelen status. Controleer de actuele scriptinhoud wanneer onduidelijk is of een actie read-only is.

## 3. Netwerk- en infrastructuurvalidatie

    ./powershell/diagnostics/Test-NetworkLabConfiguration.ps1
    ./tests/network/Test-NetworkConfiguration.ps1
    ./tests/connectivity/Test-Connectivity.ps1
    ./powershell/manage/Get-NetworkLabServices.ps1
    ./powershell/manage/Get-NetworkLabProcesses.ps1
    ./powershell/manage/Get-NetworkLabHealth.ps1

Registreer verwachte én werkelijke uitkomsten. Een foutmelding is een resultaat dat moet worden onderzocht, niet iets dat uit het rapport moet worden weggelaten.

## 4. Webapplicatie

Start de webapp volgens de actuele README vanuit de repositoryroot. De gedocumenteerde startmethode is:

    .\Run-NetworkLab.ps1

Open http://127.0.0.1:8501. Controleer de terminaluitvoer en stop de server met Ctrl+C. Stel de beheerinterface niet bloot aan een openbaar netwerk.

## 5. VirtualBox-lab controleren

    $VBoxManage = 'C:\Program Files\Oracle\VirtualBox\VBoxManage.exe'
    if (Test-Path $VBoxManage) {
        & $VBoxManage list vms
        & $VBoxManage list hostonlyifs
        & $VBoxManage list dhcpservers
    } else {
        Write-Warning 'VBoxManage.exe niet gevonden op het verwachte pad.'
    }

Controleer de VM-namen, host-only adapter, DHCP-instellingen, virtuele schijven en ISO-koppelingen. Gebruik [VM-installatiehandleiding](vm-installation-guide.md) voordat je gast-OS-installaties uitvoert.

## 6. Python-monitoring en rapportage

    python ./python/monitoring/run_monitor.py
    '[]' | python ./python/reporting/generate_report.py

Controleer de actuele scriptinterface en invoervereisten vóór uitvoering. Een lege lijst kan alleen een syntactische voorbeeldinvoer zijn en is geen echte meetdata. Gebruik voor een bewijsrapport de werkelijk verzamelde resultaten.

## 7. Configuratiewijzigingen

De baseline-configuratie is afgeschermd door veiligheidsinstellingen. Schakel die niet in voordat de echte labtopologie, interface en IP-plan zijn gecontroleerd en goedgekeurd. Leg de beginsituatie vast, wijzig één component tegelijk en test daarna opnieuw.

## 8. Bewijs vastleggen

Gebruik [Testplan](test-plan.md) en [HTML-test- en bewijsregister](test-and-evidence-register.html). Noteer datum/tijd, doel, opdracht, verwacht resultaat, werkelijk resultaat, status, foutmelding en bewijsreferentie. Laat tests openstaand zolang ze niet zijn uitgevoerd.

## Gerelateerde documentatie

- [Documentatie-index](README.md)
- [Architectuur](architecture.md)
- [Configuratie](configuration.md)
- [Monitoring](monitoring.md)
- [Troubleshooting](troubleshooting.md)
- [Beveiliging en gegevensbeheer](security-and-data-handling.md)
- [Stagecompetenties en bewijs](stage-competency-mapping.md)
