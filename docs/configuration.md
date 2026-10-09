# Configuratiehandleiding

## Doel en veiligheidsregels

Deze handleiding beschrijft de configuratie van de NetworkLab-software en het geïsoleerde VirtualBox-lab. Gebruik dit lab niet als aanleiding om instellingen op een productie- of bedrijfsnetwerk te wijzigen.

- Configuratiewijzigingen aan de Windows-host staan standaard uit.
- Controleer vóór iedere wijziging de actieve adapter, het subnet en de beoogde scope.
- Wijzig geen Wi-Fi-, Ethernet-, VPN- of bedrijfsinterface tenzij dit uitdrukkelijk is goedgekeurd.
- Sla geen wachtwoorden, tokens of privésleutels op in Git.
- Leg de oorspronkelijke toestand vast en bepaal vooraf hoe je terugdraait.

## Applicatieconfiguratie

De projectconfiguratie staat in config/lab-config.json. Lees de actuele waarden vóór gebruik:

    Get-Content .\config\lab-config.json -Raw

Laat configuratiewijzigingen uitgeschakeld zolang de interface en gewenste configuratie niet zijn gecontroleerd. Dit document vervangt de configuratie in het JSON-bestand niet.

## Netwerkparameters van het VirtualBox-lab

| Parameter | Gedocumenteerde waarde | Validatie |
|---|---|---|
| Netwerknaam | NetworkLab-Lab | Controleer in VirtualBox |
| IPv4-subnet | 192.168.77.0/24 | Controleer masker/prefix |
| Hostadapter | 192.168.77.1 | Controleer host-only adapter |
| DHCP-server | 192.168.77.2 | Controleer DHCP-configuratie |
| DHCP-pool | 192.168.77.100–192.168.77.200 | Test lease-toekenning |
| VM's | MGMT, INFRA, CLIENT | Controleer VM-namen en adapter |

Dit zijn de gedocumenteerde doelwaarden, geen bewijs van de actuele toestand. Controleer de feitelijke configuratie:

    $VBoxManage = 'C:\Program Files\Oracle\VirtualBox\VBoxManage.exe'
    & $VBoxManage list hostonlyifs
    & $VBoxManage list dhcpservers
    & $VBoxManage list vms
    Get-NetAdapter
    Get-NetIPConfiguration

## Configuratiewijzigingen

1. Noteer het doel en de verwachte uitkomst.
2. Maak een momentopname van de huidige instellingen.
3. Controleer dat alleen de bedoelde labcomponent wordt geraakt.
4. Gebruik de bedoelde NetworkLab-functie of VirtualBox-instelling.
5. Controleer de toestand direct na de wijziging.
6. Voer relevante connectiviteits- en regressietests uit.
7. Leg resultaat, tijdstip en eventuele rollback vast.

## Validatiecriteria

- Netwerknaam en subnet komen overeen met de topologie.
- De host-only adapter heeft het verwachte adres.
- DHCP-server en pool zijn zichtbaar en correct.
- Elke VM gebruikt de bedoelde host-only adapter.
- De webapp blijft bereikbaar via http://127.0.0.1:8501.
- Er zijn geen onbedoelde wijzigingen aan fysieke netwerkinterfaces.

## Terugdraaien

Gebruik de vastgelegde oude waarden en de officiële VirtualBox-interface of de bedoelde NetworkLab-functie. Verwijder geen adapter, VM of schijf voordat is gecontroleerd of deze uitsluitend bij dit lab hoort. Herhaal na rollback de inspectie- en connectiviteitstests.

## Gerelateerde documentatie

- [Virtueel netwerk](virtual-network.md)
- [Netwerktopologie](network-topology.html)
- [Installatie](installation.md)
- [Testplan](test-plan.md)
- [Beveiliging en gegevensbeheer](security-and-data-handling.md)
