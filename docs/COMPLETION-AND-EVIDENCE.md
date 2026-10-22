# NetworkLab — afrondings- en bewijschecklist

Bijgewerkt: 22 oktober 2026. Dit document maakt onderscheid tussen repositorybewijs, uitgevoerde tests en bewijs dat nog op de Windows-laptop of in het School4-dossier moet worden vastgelegd.

## 1. Gecontroleerde projectstatus

| Onderdeel | Status | Bewijs / grens |
|---|---|---|
| Client UI op 127.0.0.1:8510 | Geslaagd | Runtime-test meldde HTTP 200 |
| Management UI op 127.0.0.1:8511 | Geslaagd | Runtime-test meldde HTTP 200 |
| Infrastructure UI op 127.0.0.1:8512 | Geslaagd | Runtime-test meldde HTTP 200 |
| Infrastructure `/api/health` | Geslaagd | HTTP 200 en JSON-status `ok` |
| Infrastructure `/api/status` | Geslaagd | HTTP 200 en JSON-status `ok` |
| Git-synchronisatie | Geslaagd bij laatste lokale controle | Feature-branch was schoon en gelijk aan origin |
| Automatisch herstel | Gedeeltelijk bewezen | Taak/supervisor eerder actief gezien; herstel na echte Windows-herstart moet nog aantoonbaar worden getest |
| Schoolbeoordeling | Niet automatisch bewezen | De beoordelingscriteria van de opleiding moeten naast dit technische bewijs worden gelegd |

Runtime-resultaten zijn momentopnamen. Bewaar het actuele JSON-rapport lokaal in `evidence/runtime/` en maak een screenshot van de testuitvoer voor het bewijsdossier.

## 2. B1-K2-W1 — installeren en configureren

**Technisch bewijs aanwezig:** projectstructuur, startscript, drie afzonderlijke webapps, lokale poorten, read-only Infrastructure API, architectuurdocumentatie en netwerktekening.

**Nog persoonlijk vast te leggen voor het dossier:**
- Screenshot van de drie geopende webapps.
- Screenshot van de geslaagde runtime-test (alle vijf controles).
- Leg vast welke configuratie je zelf hebt ingesteld, waarom de services aan `127.0.0.1` binden en hoe de drie apps met elkaar communiceren.
- Controleer de officiële opdracht/rubric: als VirtualBox of een echte VM expliciet verplicht is, voldoet de huidige no-VM-variant daar niet vanzelf aan.

## 3. B1-K2-W2 — beheren, monitoren en storingen oplossen

**Technisch bewijs aanwezig:** health checks, HTTP/API-tests, logbestanden, supervisor- en herstelscripts en een automatische hersteltaak.

**Nog uit te voeren en te documenteren op de laptop:**
1. Voer `Test-NetworkLabWebApps.ps1` uit en bewaar het JSON-rapport.
2. Stop alleen voor een gecontroleerde test één NetworkLab-app-proces; noteer tijdstip en verwachte impact.
3. Laat de herstelbewaking de app opnieuw starten en voer de vijf controles opnieuw uit.
4. Leg voor/na-resultaat en relevante logregels vast.
5. Herstart Windows en controleer opnieuw dat alle drie apps bereikbaar zijn en dat de taak/supervisor draait. Alleen een succesvolle herstarttest bewijst autostart na reboot.

Voer geen storingsproef uit op een ander proces of op een poort die niet aantoonbaar bij NetworkLab hoort.

## 4. Beveiligingsgrenzen en tests

De huidige implementatie is een lokale, read-only labdemo — geen productiebeveiligingsoplossing en geen vervanging voor de officiële security-rubric.

- De webservers en API binden aan loopback (`127.0.0.1`); niet bedoeld voor toegang vanaf het LAN.
- De API biedt alleen status-/health-routes; onbekende routes horen HTTP 404 te geven.
- CORS staat alleen de Client- en Management-origin toe; een vreemde origin mag niet worden teruggestuurd.
- De API voert geen shell-/PowerShell-opdrachten uit en wijzigt geen hostconfiguratie.
- Er zijn geen authenticatie- of autorisatievoorzieningen voor gebruik door meerdere gebruikers; houd de service lokaal.
- Voer de geautomatiseerde tests uit met `python -m unittest discover -s tests -p "test_*.py" -v` en controleer ook de PowerShell-syntaxis via de GitHub Actions-workflow.

## 5. B1-K3-W1/W2 — uitvoeringsbewijs

In eerdere sessies is gemeld dat beide PowerShell-tests slaagden. De resterende administratieve stap was de screenshots van beide resultaten in de project-/inlevermap te bewaren. Dit repositorydocument vervangt die screenshots of het vereiste School4-bewijs niet.

## 6. Inlevercontrole

- [ ] Officiële beoordelingscriteria/rubrics toegevoegd of vergeleken.
- [ ] Screenshot van alle drie webapps.
- [ ] Screenshot en JSON van 5/5 runtime-controles.
- [ ] Bewijs van gecontroleerde storing en herstel.
- [ ] Bewijs van autostart na Windows-herstart.
- [ ] Screenshots van B1-K3-W1 en B1-K3-W2 in de juiste inlevermap.
- [ ] Bewijs gecontroleerd op wachtwoorden, tokens en onbedoelde persoonsgegevens/lokale gegevens.

Een vinkje mag pas worden gezet nadat het betreffende bewijs werkelijk is vastgelegd.
