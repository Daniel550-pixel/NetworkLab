# Testplan NetworkLab

## Doel

Dit plan beschrijft hoe de webapp, hostinspectie, VirtualBox-lab en connectiviteit gecontroleerd kunnen worden. Voer tests in volgorde uit en noteer de echte resultaten. De aanwezigheid van een script is niet hetzelfde als een geslaagde test.

## Statuswaarden

- Openstaand — nog niet uitgevoerd.
- Geslaagd — uitgevoerd en voldoet aan het criterium.
- Mislukt — uitgevoerd en voldoet niet aan het criterium.
- Geblokkeerd — niet uitgevoerd door een technische of veiligheidsbeperking.

## Testgevallen

| ID | Test | Procedure | Acceptatiecriterium | Beginstatus |
|---|---|---|---|---|
| NL-01 | Repositorycontrole | git status en controle van benodigde bestanden | Werkmap bekend; wijzigingen geïdentificeerd | Openstaand |
| NL-02 | Webapp start | Start volgens README en open localhost | Server start zonder traceback; UI laadt | Openstaand |
| NL-03 | Lokale grens | Controleer serveradres en poort | UI gebonden aan localhost zoals bedoeld | Openstaand |
| NL-04 | Configuratieveiligheid | Lees config/lab-config.json | Wijzigingen standaard uitgeschakeld | Openstaand |
| NL-05 | PowerShell-inspectie | Voer read-only status- en adapterchecks uit | Uitvoer beschikbaar zonder onverwachte wijziging | Openstaand |
| NL-06 | VirtualBox-installatie | VBoxManage --version | Versie wordt gerapporteerd | Openstaand |
| NL-07 | Host-only netwerk | Inspecteer hostonlyifs en DHCP | Naam, subnet, hostadres en pool komen overeen | Openstaand |
| NL-08 | VM-inventaris | VBoxManage list vms | Drie bedoelde VM's zijn aanwezig | Openstaand |
| NL-09 | VM-start | Start elke VM via de afgesproken bediening | VM start vanaf de bedoelde virtuele schijf | Openstaand |
| NL-10 | Gast-DHCP | Controleer ip -brief address in elke gast | Uniek adres in afgesproken pool | Openstaand |
| NL-11 | Host naar gast | Test werkelijk gast-IP vanaf Windows | Bereikbaarheid aantoonbaar; ICMP-resultaat correct geïnterpreteerd | Openstaand |
| NL-12 | Gast naar gast | Test twee gasten in beide richtingen waar passend | Resultaat en eventuele firewallbeperking vastgelegd | Openstaand |
| NL-13 | Rapportage | Voer monitoring/rapportage uit met werkelijke invoer | Rapport bevat bron, tijd en waargenomen resultaat | Openstaand |
| NL-14 | Regressie | Herhaal relevante checks na wijziging | Geen onbedoelde regressie | Openstaand |

## Uitvoeringsformulier

Voor elke test leg je vast:
- test-ID;
- datum en lokale tijd;
- Windows-, Python-, PowerShell- en VirtualBox-versie indien relevant;
- commando of procedure;
- verwacht resultaat;
- werkelijk resultaat en volledige foutmelding;
- status;
- bewijsbestandsnaam;
- conclusie en vervolgactie.

## Testveiligheid

- Begin met read-only controles.
- Voer configuratiewijzigingen alleen binnen de lab-scope uit.
- Gebruik geen echte credentials in voorbeelden of bewijs.
- Verwijder geen VM, adapter, schijf of configuratie om een test te laten slagen.
- Als de test risico oplevert of scope onduidelijk is, markeer als Geblokkeerd.

## Resultaten

De beginstatus van alle bovenstaande tests is Openstaand. Werk deze tabel of het [HTML-test- en bewijsregister](test-and-evidence-register.html) pas bij nadat de test werkelijk is uitgevoerd.
