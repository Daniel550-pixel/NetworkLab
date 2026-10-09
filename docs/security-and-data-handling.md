# Beveiliging en gegevensbeheer

## Doel

NetworkLab is bedoeld voor lokaal leren, beheer en gecontroleerde tests. De veiligheidsmaatregelen voorkomen dat een test onbedoeld een productieomgeving raakt of gevoelige gegevens in de repository terechtkomen.

## Netwerkgrenzen

- De webapp hoort bereikbaar te zijn via 127.0.0.1.
- Het VM-lab gebruikt de VirtualBox host-only netwerkmodus.
- De gedocumenteerde topologie vereist geen fysieke bridge naar het thuis- of bedrijfsnetwerk.
- Schakel geen bridge, port-forwarding of externe toegang in zonder expliciete opdracht en risicoanalyse.
- Controleer de feitelijke instellingen; vertrouw niet uitsluitend op een diagram.

## Least privilege

- Gebruik een standaardaccount waar mogelijk.
- Voer PowerShell als administrator alleen uit wanneer de taak dat werkelijk vereist.
- Controleer iedere opdracht die adapters, services, firewallregels, routes, VM's of virtuele schijven kan wijzigen.
- Gebruik geen verwijder- of resetcommando's als eerste diagnostische stap.

## Geheimen en persoonsgegevens

Commit of deel nooit:
- wachtwoorden of herstelcodes;
- API-tokens, sessiecookies of private sleutels;
- persoonlijke identificatiegegevens die niet nodig zijn voor de opdracht;
- screenshots waarop credentials, persoonlijke bestanden of gevoelige netwerkdetails zichtbaar zijn.

Gebruik voor screenshots en rapporten alleen de informatie die nodig is om de test aan te tonen. Redigeer irrelevante gegevens.

## Logs en bewijs

Bewaar bij bewijs de context die nodig is om het resultaat te reproduceren, maar geen secrets. Gebruik betekenisvolle bestandsnamen, bijvoorbeeld datum-component-test. Controleer bestanden vóór commit:

    git status --short
    git diff --check

Controleer ook of nieuw toegevoegde logs geen tokens of wachtwoorden bevatten.

## Configuratie en wijzigingscontrole

- Netwerkwijzigingen staan standaard uit.
- De echte interface moet expliciet worden gekozen.
- Inspectie en bewijsverzameling gaan vooraf aan wijziging.
- Noteer de oorspronkelijke toestand en een rollbackplan.
- Valideer de toestand na iedere wijziging.

## Incidentrespons

Bij een onbedoelde wijziging:
1. Stop verdere wijzigingen.
2. Leg de actuele toestand vast.
3. Identificeer de betrokken component.
4. Herstel de vorige toestand met een gecontroleerde procedure.
5. Test opnieuw en noteer de uitkomst.
6. Meld eventuele impact aan de verantwoordelijke begeleider.

## Grenzen

Deze documentatie is geen formele security-audit en bewijst niet dat alle implementaties beveiligingsgetest zijn. Beoordeel de actuele code, configuratie en omgeving vóór gebruik buiten een geïsoleerd lab.
