# NetworkLab

## Stage Project — Network & Infrastructure Management

NetworkLab is een gecontroleerd lokaal lab voor het installeren, configureren, beheren en monitoren van netwerk- en infrastructuuronderdelen.

De documentatie en projectbestanden ondersteunen twee in het project gebruikte stagewerkprocessen:
1. **B1-K2-W1 — Installeert en configureert netwerk- en infrastructuuronderdelen**
2. **B1-K2-W2 — Beheert en monitort netwerk- en infrastructuuronderdelen**

Controleer de officiële beoordelingscriteria met de school of stagebegeleider. Scripts en documentatie zijn geen vervanging voor aantoonbaar uitgevoerde werkzaamheden.

## Technology Stack

| Technologie | Doel |
|---|---|
| GitHub | Versiebeheer, implementatie, documentatie en bewijs |
| Python | Lokale HTTP-server, monitoring, diagnostiek en rapportage |
| HTML/CSS/JavaScript | Lokale webinterface |
| PowerShell | Windows-netwerkinspectie, veiligheidscontroles en diagnostiek |
| JSON | Labconfiguratie en gestructureerde gegevens |
| VirtualBox | Geïsoleerde virtuele netwerk- en VM-omgeving |
| GitHub Actions | Geautomatiseerde validatie volgens de workflows |

## Lokale webapplicatie

De NetworkLab-interface is een localhost-webapplicatie.

- Geen Streamlit-runtime vereist.
- Geen externe frontend-CDN vereist volgens het projectontwerp.
- De Python-standaardbibliotheek levert de lokale HTTP-server.
- De browserinterface is bedoeld voor 127.0.0.1.
- De UI-bestanden staan in web/.
- De server-entrypoint is app/server.py.

### Starten

Voer vanuit de repositoryroot in PowerShell uit:

    .\Run-NetworkLab.ps1

Open vervolgens http://127.0.0.1:8501. Gebruik een aangepaste poort alleen als de huidige launcher die optie ondersteunt. Als de launcher ontbreekt, controleer dan eerst de actuele repositorybestanden.

## Webapplicatieonderdelen

- Command Center
- Topology
- Interfaces
- Addressing
- Connectivity
- Services
- Diagnostics
- Evidence
- VM storage & OS media

De applicatieweergave en de echte host-/VM-status moeten met de onderliggende observaties worden vergeleken.

## Netwerktopologie en VM-lab

De gedocumenteerde VirtualBox host-only topologie gebruikt de volgende doelwaarden:

| Onderdeel | Gedocumenteerde waarde |
|---|---|
| Netwerknaam | NetworkLab-Lab |
| Subnet | 192.168.77.0/24 |
| Hostadres | 192.168.77.1 |
| DHCP-server | 192.168.77.2 |
| DHCP-pool | 192.168.77.100–192.168.77.200 |
| VM's | NetworkLab-VM01-MGMT, NetworkLab-VM02-INFRA, NetworkLab-VM03-CLIENT |
| Virtuele schijf | 20 GB VDI per VM, volgens de projectdocumentatie |

Dit zijn gedocumenteerde doelwaarden. Controleer ze tegen de actuele VirtualBox-configuratie. Gast-IP-adressen en end-to-end-connectiviteit moeten na installatie worden gemeten; vul geen niet-waargenomen waarden in.

## Veiligheidsmodel

- Netwerkwijzigingen blijven standaard uitgeschakeld in config/lab-config.json.
- Configuratieacties vereisen een expliciete lab-scope.
- Begin met read-only inspectie.
- Gebruik geen fysieke LAN-bridge of productieconfiguratie als impliciete aanname.
- Commit geen wachtwoorden, tokens of privésleutels.
- Een gesimuleerde incidentstatus is geen bewijs van een echte storing.

## Documentatie

De volledige documentatie-index staat in [docs/README.html](docs/README.html).

Belangrijkste documenten:
- [Architectuur en componenten](docs/architecture.html)
- [Installatiehandleiding](docs/installation.html)
- [Configuratiehandleiding](docs/configuration.html)
- [HTML/SVG-netwerktopologie](docs/network-topology.html)
- [Virtueel netwerk](docs/virtual-network.html)
- [VM-installatiehandleiding](docs/vm-installation-guide.html)
- [VM-opslag en ISO-media](docs/vm-storage.html)
- [Runbook](docs/runbook.html)
- [Monitoring en diagnostiek](docs/monitoring.html)
- [Troubleshooting](docs/troubleshooting.html)
- [Beveiliging en gegevensbeheer](docs/security-and-data-handling.html)
- [Testplan](docs/test-plan.html)
- [HTML-test- en bewijsregister](docs/test-and-evidence-register.html)
- [Koppeling stagecompetenties aan bewijs](docs/stage-competency-mapping.html)
- [Bestaand stagebewijsregister](docs/evidence.html)
- [Begrippenlijst](docs/glossary.html)

## Uitvoeringsvolgorde

1. Controleer de repository en lokale vereisten.
2. Start de lokale NetworkLab-webapp.
3. Inspecteer de actuele host- en VirtualBox-status.
4. Vergelijk de werkelijke omgeving met de topologie.
5. Voer alleen goedgekeurde configuratiestappen uit binnen de lab-scope.
6. Valideer adressering en connectiviteit.
7. Voer monitoring en rapportage uit.
8. Bewaar resultaten en bewijs.
9. Werk documentatie bij op basis van de waarnemingen.

## Teststatus en beperkingen

De handleidingen en registratieformulieren zijn documentatie en uitvoeringshulpmiddelen. Ze bewijzen niet dat een gast-OS is geïnstalleerd, DHCP werkt of VM's onderling bereikbaar zijn. De tests in [docs/test-plan.html](docs/test-plan.html) beginnen op **Openstaand** en mogen pas na daadwerkelijke uitvoering worden bijgewerkt.

