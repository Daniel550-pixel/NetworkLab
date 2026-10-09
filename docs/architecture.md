# Architectuur van NetworkLab

## 1. Overzicht

NetworkLab combineert een lokale webinterface met PowerShell-diagnostiek, Python-monitoring en optionele VirtualBox-labfuncties. De onderdelen zijn bedoeld om netwerk- en infrastructuurstatus zichtbaar en controleerbaar te maken.

## 2. Logische componenten

| Component | Locatie | Verantwoordelijkheid |
|---|---|---|
| Lokale HTTP-server | app/server.py | Serveert webbestanden en lokale API-routes |
| Webinterface | web/ | Dashboard, statusweergave en gebruikersbediening |
| Labconfiguratie | config/lab-config.json | Veiligheidsinstellingen en labparameters |
| PowerShell-tools | powershell/ | Windows-netwerkinspectie, beheer en diagnostiek |
| Python-monitoring | python/monitoring/ | Periodieke of handmatige statusverzameling |
| Python-diagnostiek | python/diagnostics/ | Gerichte netwerkdiagnostiek |
| Rapportage | python/reporting/ | Resultaten verwerken en rapporten schrijven |
| Tests | tests/ | Controle van netwerk-, connectiviteits- en infrastructuurgedrag |
| Documentatie | docs/ | Procedures, topologie en bewijsregistratie |
| CI | .github/workflows/ | Automatische validatie volgens workflowconfiguratie |

Controleer de actuele bestandsstructuur in de repository; deze tabel is de logische architectuur en geen garantie dat iedere module in elke branch aanwezig is.

## 3. Gegevensstroom

    Beheerder
       |
       v
    Browser: http://127.0.0.1:8501
       |
       v
    Lokale HTTP-server (app/server.py)
       |                         |
       v                         v
    web/ UI                lokale API-routes
                                 |
                 +---------------+---------------+
                 |               |               |
                 v               v               v
            hoststatus       VirtualBox       labconfig
                 |               |               |
                 +---------------+---------------+
                                 |
                                 v
                         status in de UI

PowerShell- en Python-tools kunnen afzonderlijk worden uitgevoerd om observaties te verzamelen en resultaten vast te leggen. Een rapport hoort gebaseerd te zijn op de werkelijk verzamelde gegevens.

## 4. Lokale netwerkgrens

De webapp is ontworpen voor localhost-gebruik via 127.0.0.1. Gebruik deze interface niet als publiek toegankelijke beheersconsole. De applicatie-laag en het VirtualBox host-only lab zijn verschillende netwerkgrenzen:
- localhost is voor de browserinterface op de host;
- NetworkLab-Lab is het virtuele segment voor de gastmachines;
- de documentatie gaat niet uit van een fysieke LAN-bridge.

## 5. Veiligheidsontwerp

- Netwerkwijzigingen zijn standaard uitgeschakeld in de labconfiguratie.
- Configuratieacties moeten een expliciete scope gebruiken.
- Inspectie gaat vooraf aan configuratie.
- Geen automatische OS-downloads of externe ISO-selectie worden verondersteld.
- Werkelijke observaties worden onderscheiden van gesimuleerde gebeurtenissen.
- Geheimen horen niet in broncode, commits, logs of screenshots.

## 6. Foutisolatie

Onderzoek problemen in deze volgorde:
1. Browser en localhost-poort.
2. HTTP-server en terminaluitvoer.
3. API- of applicatielaag.
4. Hostnetwerk en adapterstatus.
5. VirtualBox host-only segment.
6. Gast-OS, DHCP en guest-to-guest-connectiviteit.

Zie [Troubleshooting](troubleshooting.md) voor concrete controles.
