# Bewijsmatrix stageopdracht — B1-K2-W1/W2

> **Let op:** gebruik de officiële beoordelingsformulieren van school en stagebedrijf als leidend document. De onderstaande werkprocesnamen volgen de omschrijving in de huidige NetworkLab-README; controleer of de formulering exact overeenkomt met jouw kwalificatiedossier.

## Projectcontext

NetworkLab is een lokale, gecontroleerde labomgeving voor het installeren/configureren en beheren/monitoren van netwerk- en infrastructuuronderdelen. De applicatie draait lokaal op `127.0.0.1:8501`; VirtualBox biedt de virtuele labomgeving. Wijzigingen aan netwerken zijn standaard beveiligd en horen alleen plaats te vinden wanneer de labtopologie bekend is en de veiligheidsvoorwaarden zijn gecontroleerd.

## B1-K2-W1 — Installeren en configureren van netwerk- en infrastructuuronderdelen

| Bewijsstuk | Wat het aantoont | Wat nog vastgelegd moet worden |
|---|---|---|
| [Netwerktopologie (HTML)](network-topology.html) | De host, host-only verbinding, subnet en rollen van de VM's zijn inzichtelijk gemaakt. | Werkelijke adaptergegevens, VM-namen, gast-IP's en eventueel gateway/DNS invullen na controle. |
| Project-README | Startprocedure, technologieën, projectonderdelen en veiligheidsmodel zijn beschreven. | Screenshots van de daadwerkelijke werkende applicatie en relevante VirtualBox-instellingen toevoegen. |
| [Verificatieformulier](verification-record-template.md) | Een vaste registratie van host-, VM-, adresserings-, connectiviteits- en veiligheidscontroles. | Vul het formulier pas na daadwerkelijke controle in en voeg relevante, opgeschoonde bewijsstukken toe. |
| PowerShell- en VirtualBox-controles | Een reproduceerbare controle van adapters, VM's en configuratie is mogelijk. | Datum, uitvoer en eventuele afwijkingen opslaan als bewijsstuk. |
| Configuratiebestanden | De labconfiguratie en veiligheidsvoorwaarden zijn als bestanden te controleren. | Noteer welke instellingen zijn aangepast, waarom en hoe de wijziging is gevalideerd. |

### Uit te voeren verificaties

- [ ] Controleer met `Get-NetIPConfiguration` het hostadres en de actieve adapters.
- [ ] Controleer met `VBoxManage list hostonlyifs` de host-only adapter.
- [ ] Controleer met `VBoxManage list vms` de exacte VM-namen.
- [ ] Controleer per VM met `VBoxManage showvminfo "EXACTE-VM-NAAM"` de gekoppelde netwerkadapter.
- [ ] Controleer binnen iedere gastmachine het IP-adres, subnetmasker, gateway en DNS.
- [ ] Leg de werkelijke resultaten vast met datum en korte conclusie.
- [ ] Controleer na configuratie dat de beoogde verbindingen werken en dat niet-bedoelde netwerkverbindingen niet zijn ontstaan.

## B1-K2-W2 — Beheren en monitoren van netwerk- en infrastructuuronderdelen

| Bewijsstuk | Wat het aantoont | Wat nog vastgelegd moet worden |
|---|---|---|
| Incident- en monitoringdocumentatie | Een reproduceerbare gesimuleerde incidentcyclus, detectie en logging zijn beschreven. | Voeg de testuitvoer of schermafbeeldingen toe aan het bewijspakket, zonder gevoelige gegevens. |
| `Invoke-NetworkLabIncidentSimulation.ps1` en de integratietest | De incidentacties bewaken de statusvolgorde; de geautomatiseerde test controleert lifecycle, logging, detectie, herstel en afwijzing van een ongeldige volgorde. | Voeg bewijs toe van de geslaagde GitHub Actions-run en breid tests uit voor ontbrekende/ongeldige statusbestanden. |
| `Start-NetworkLabMonitoringFeed.ps1` | De feed leest periodiek de simulatiestatus en registreert een detectie-event. | Documenteer dat de huidige feed een bestandssimulatie is, geen echte netwerkprobe. |
| JSONL-gebeurtenislogs | Gebeurtenissen kunnen achteraf worden onderzocht. | Bewaar alleen relevante, opgeschoonde logs en noteer welke conclusie uit elk log volgt. |
| NetworkLab-webapp | De lokale UI bevat onder andere topology, interfaces, addressing, connectivity, diagnostics en evidence-secties. | Leg per gebruikte functie vast wat je hebt gecontroleerd en wat het resultaat was. |

### Uitgevoerde controles

- De vier incidentacties zijn lokaal in de juiste volgorde uitgevoerd; de status keerde na `Verify` terug naar `normal`.
- De monitoringfeed heeft de status `fault_injected` waargenomen en een `DETECTED`-event met `simulation: true` vastgelegd.
- De integratietest controleert lifecycle-volgorde, eventregistratie, detectie, eindstatus en afwijzing van een ongeldige actievolgorde.
- De GitHub Actions-workflow voert deze integratietest uit op pushes naar `main` en `feature/vm-readiness`, en bij pull requests naar `main`. Controleer de run voor de commit die je als bewijs gebruikt.
- Tests herstellen de bestanden die ze tijdelijk aanpassen. De simulatie bewijst geen werkelijke netwerkonderbreking of live monitoring.

## Werkwijze voor een bruikbaar bewijsstuk

Leg per opdracht of wijziging steeds vast:

1. **Doel:** wat moest worden geïnstalleerd, geconfigureerd, beheerd of gecontroleerd?
2. **Beginsituatie:** welke hardware, VM, adapter, IP-configuratie of service was aanwezig?
3. **Uitvoering:** welke concrete handelingen en commando's zijn uitgevoerd?
4. **Resultaat:** wat kwam er uit de controle, en voldoet dat aan het doel?
5. **Afwijking en oplossing:** wat ging niet goed, hoe is dat onderzocht en opgelost?
6. **Veiligheid:** welke risico's zijn beperkt en hoe is voorkomen dat de productieomgeving werd beïnvloed?
7. **Bewijs:** datum, screenshots of relevante logregels, met gevoelige informatie verwijderd.
8. **Reflectie:** wat zou je bij een volgende uitvoering verbeteren?

## Openstaande punten vóór definitieve beoordeling

- [ ] Vergelijk de werkprocesnamen en beoordelingscriteria met het officiële formulier van de opleiding.
- [ ] Vervang de voorlopige netwerkweergave door een geverifieerde as-built-tekening.
- [ ] Vul [het verificatieformulier](verification-record-template.md) in met de werkelijke resultaten en verwijs naar de bijbehorende bewijsbestanden.
- [ ] Voeg schermafbeeldingen toe van de webapp en de daadwerkelijke VirtualBox-configuratie.
- [ ] Bewaar representatieve testuitvoer, maar commit geen tijdelijke runtime-logs zonder reden.
- [ ] Laat een begeleider controleren of ieder bewijsstuk direct aansluit op een beoordelingsindicator.

**Beoordelingsgrens:** documentatie en gesimuleerde tests ondersteunen het bewijs, maar zijn op zichzelf geen bewijs dat alle handelingen op echte infrastructuur zijn uitgevoerd. Maak steeds duidelijk wat echt is geconfigureerd en wat alleen is gesimuleerd.
