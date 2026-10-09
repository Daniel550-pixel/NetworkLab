# Operationeel beheer van NetworkLab

## Routinebeheer

1. Controleer de repositorystatus en documentatieversie.
2. Start de webapp alleen wanneer deze nodig is.
3. Controleer netwerk- en infrastructuurstatus voordat je wijzigingen uitvoert.
4. Voer tests uitsluitend binnen de geïsoleerde lab-scope uit.
5. Bewaar logs en bewijs met datum, context en resultaat.
6. Registreer fouten en wijzigingen zodat de uitvoering reproduceerbaar is.

## Status inspecteren

Voer uit vanuit de repositoryroot en controleer eerst of de scripts aanwezig zijn in de huidige checkout:

    git status --short --branch
    ./powershell/configure/Get-NetworkLabState.ps1
    ./powershell/configure/Get-NetworkConfiguration.ps1
    ./powershell/manage/Get-NetworkLabServices.ps1
    ./powershell/manage/Get-NetworkLabProcesses.ps1
    ./powershell/manage/Get-NetworkLabHealth.ps1

Als een opdracht faalt, noteer de volledige foutmelding en het gebruikte pad.

## Beheer van VirtualBox-lab

Gebruik de NetworkLab-webapp om de actuele virtuele netwerk- en VM-status te bekijken. Controleer VM-naam, netwerkadapter, opslag en ISO-koppeling vóór start- of opslagacties. Gebruik geen verwijdercommando's voor VM's, schijven of snapshots zonder expliciete controle van het doel.

## Onderhoud

- Werk documentatie bij wanneer configuratie of procedures veranderen.
- Test scripts na wijzigingen.
- Houd Windows-, Python-, PowerShell- en VirtualBox-versies bij.
- Controleer dat bewijs geen geheimen of onnodige persoonsgegevens bevat.
- Verwijder oude logs pas nadat is vastgesteld dat ze niet meer nodig zijn.

## Wijzigingsregistratie

| Veld | In te vullen |
|---|---|
| Datum/tijd | Lokale datum en tijd |
| Aanleiding | Waarom de wijziging nodig was |
| Component | Script, configuratie, VM of netwerk |
| Voor/na | Waargenomen toestand vóór en na |
| Test | Uitgevoerde validatie |
| Resultaat | Geslaagd, mislukt of geblokkeerd |
| Terugvalplan | Hoe de vorige toestand wordt hersteld |

## Incidentprocedure

1. Stop verdere wijzigingen.
2. Verzamel foutmelding en actuele status.
3. Bepaal of de oorzaak bij webapp, host, VirtualBox, gast-OS of netwerk ligt.
4. Voer één gecontroleerde diagnostische stap tegelijk uit.
5. Herstel alleen de component die aantoonbaar de oorzaak is.
6. Herhaal de oorspronkelijke test en registreer de uitkomst.

Zie [Runbook](runbook.md), [Monitoring](monitoring.md) en [Troubleshooting](troubleshooting.md).
