# WiFi Profile Manager

Een lokale Windows-GUI-applicatie in Python/Tkinter voor het bekijken en beheren van opgeslagen wifi-profielen.

## Functies
- Lijst met opgeslagen wifi-profielen.
- Profiel- en beveiligingsdetails bekijken.
- Wachtwoord standaard verborgen; zichtbaar maken vereist een expliciete bevestiging.
- Wifi-interface-informatie bekijken.
- Een opgeslagen profiel verwijderen na een bevestigingsvenster.
- Geen externe netwerkverbindingen en geen opslag van wachtwoorden/logbestanden.

## Vereisten
- Windows 10 of Windows 11
- Python 3.10+ (Tkinter inbegrepen bij de standaard Windows-installatie van Python)

## Starten
1. Pak de ZIP uit naar een map die je zelf kiest.
2. Open PowerShell in die map.
3. Voer uit:

   ```powershell
   py .\wifi_profile_manager.py
   ```

De applicatie gebruikt `netsh wlan`, dat bij Windows hoort. Sommige gegevens kunnen afhankelijk zijn van Windows-rechten, beleid en de netwerkconfiguratie niet beschikbaar zijn.

## Optioneel: een EXE bouwen
Installeer PyInstaller:

```powershell
py -m pip install pyinstaller
py -m PyInstaller --onefile --windowed --name WiFiProfileManager .\wifi_profile_manager.py
```

De EXE verschijnt daarna in de map `dist`.

## Beveiliging
Gebruik dit alleen op een Windows-computer en voor wifi-profielen die je bevoegd bent te beheren. Een opgeslagen sleutel kan gevoelige informatie zijn. Deel geen screenshots waarin wachtwoorden zichtbaar zijn.
