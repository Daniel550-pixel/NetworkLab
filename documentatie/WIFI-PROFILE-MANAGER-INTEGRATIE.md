# NetworkLab-webapps in WiFi Profile Manager

## Doel

De WiFi Profile Manager-GUI biedt toegang tot de statuscontrole van de drie lokale NetworkLab-webapps.

## Services

- Client: http://127.0.0.1:8510
- Management: http://127.0.0.1:8511
- Infrastructure API: http://127.0.0.1:8512

## Gebruik

1. Start de WiFi Profile Manager.
2. Open NetworkLab-webapps.
3. Klik op Controleer verbindingen.
4. Gebruik Open om een webapp in de standaardbrowser te openen.

## Betekenis van de status

ONLINE betekent dat een HTTP-respons is ontvangen. Dit is een bereikbaarheidstest, geen volledige controle van alle interne functionaliteit.

## Implementatie

- apps/wifi-profile-manager/wifi_profile_manager.py
- apps/wifi-profile-manager/networklab_status.py

De statuscontrole gebruikt time-outs en voert netwerkverzoeken buiten de GUI-thread uit.
