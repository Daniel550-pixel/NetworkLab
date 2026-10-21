# NetworkLab

NetworkLab is een lichtgewicht lokaal netwerk- en infrastructuurdashboard met drie afzonderlijke webapps. De huidige architectuur vereist **geen VirtualBox, geen virtuele machines en geen externe frontend-CDN's**.

## Apps

| App | Lokale URL | Doel |
|---|---|---|
| Client | http://127.0.0.1:8510 | Gebruikersportaal en verbindingstest |
| MGMT | http://127.0.0.1:8511 | Centraal overzicht en read-only health checks |
| INFRA | http://127.0.0.1:8512 | Python-standaardbibliotheek API en service-status |

## Starten op Windows

Vereisten: Python 3 en Windows PowerShell.

Voer vanuit de repositoryroot uit:

    .\Run-NetworkLab-WebApps.ps1

Open daarna de drie lokale URL's hierboven. De launcher controleert eerst of de poorten vrij zijn. Logs worden in logs/ geplaatst.

## Architectuur

- apps/client/: zelfstandige statische Client UI.
- apps/mgmt/: zelfstandige statische Management UI.
- apps/infra/: zelfstandige Infrastructure UI en API, gebouwd met Python's standaardbibliotheek.
- Client en MGMT vragen status op bij INFRA via HTTP.
- Alle services binden standaard aan 127.0.0.1; ze worden niet openbaar op het LAN aangeboden.
- Er zijn geen externe JavaScript- of CSS-CDN's nodig.
- De Infrastructure API voert geen shell- of PowerShell-opdrachten uit en wijzigt geen hostconfiguratie.

## API

- GET /api/health — minimale health check.
- GET /api/status — status, platform, Python-runtime en architectuurmodus.
- GET /healthz — alternatieve health-checkroute.

## Veiligheidsgrenzen

Deze eerste versie is bewust read-only. Er zijn geen VM-start/stop-acties, virtuele netwerkacties, ISO-koppelingen of hostwijzigingen. De oude VM-gerichte code en documentatie kunnen nog in de repository staan, maar zijn geen onderdeel van de nieuwe launcher. Verwijdering van legacy-code gebeurt pas na afzonderlijke review.

## Stage-documentatie

De bestaande documentatie rond B1-K2-W1 en B1-K2-W2 kan worden aangepast aan de nieuwe scope: webapps, servicebeschikbaarheid, API-controles, logging en testbewijs. Documentatie geldt niet als bewijs van een test die niet daadwerkelijk is uitgevoerd.
