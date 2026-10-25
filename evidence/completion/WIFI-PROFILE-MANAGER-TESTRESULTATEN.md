# WiFi Profile Manager — test- en bewijsrapport

- Datum rapportage: 2026-10-25 20:41:47
- Repository: C:\Users\Daan Salden\Downloads\NetworkLab
- Git-branch: feature/three-webapps-no-vms
- HEAD bij rapportage: 98506d0

## 1. Projectintegratie
- [x] Bronbestanden gecontroleerd.
- [x] Applicatiebestanden in apps/wifi-profile-manager geplaatst
      of inhoudelijk gelijk bevonden aan de bronbestanden.
- [x] Integratiedocumentatie geschreven.

## 2. Geautomatiseerde controle
- Python AST-syntaxiscontrole: GESLAAGD.
- De controle bewijst alleen dat het Python-bestand syntactisch
  kan worden geparseerd. Zij bewijst geen volledige runtimewerking.

## 3. Handmatig waargenomen resultaat
De gebruiker heeft gemeld dat de grafische interface op Windows
start en heeft uitvoer gedeeld voor het opgeslagen profiel
'wifi Daan' op interface 'Wi-Fi 2'.

In die uitvoer:
- werden profiel- en verbindingsinstellingen getoond;
- werden WPA3-Personal- en WPA2-Personal-mogelijkheden vermeld;
- stond dat een beveiligingssleutel aanwezig is;
- bleef de sleutelinhoud in de gedeelde uitvoer verborgen.

Status: handmatig resultaat gerapporteerd door gebruiker;
niet onafhankelijk opnieuw uitgevoerd door dit integratiescript.

## 4. Nog afzonderlijk te testen
- [ ] Vernieuwen van de profielenlijst.
- [ ] Wifi-interface-informatie via de GUI.
- [ ] Wachtwoord blijft verborgen in de standaardweergave.
- [ ] Wachtwoord weergeven en daarna opnieuw verbergen.
- [ ] Verwijderactie alleen indien veilig en noodzakelijk.
- [ ] De drie bestaande NetworkLab-webapps afzonderlijk controleren.

## 5. Screenshots
Bewaar echte screenshots in evidence/screenshots/.
Er zijn door dit script geen screenshots verzonnen of aangemaakt.
Verwijder of vervaag wachtwoorden en andere gevoelige gegevens
voordat screenshots worden opgeslagen of ingeleverd.

## Conclusie
De applicatiebestanden zijn in de repository geïntegreerd en de
Python-syntaxiscontrole is uitgevoerd. De GUI-uitvoer is door de
gebruiker gerapporteerd. De overige tests zijn pas geslaagd nadat
ze daadwerkelijk zijn uitgevoerd en gecontroleerd.
