# Troubleshooting-playbook

## Algemene werkwijze

1. Noteer wat je verwachtte en wat werkelijk gebeurde.
2. Bewaar de volledige foutmelding, tijdstip en gebruikte opdracht.
3. Verander maar één variabele tegelijk.
4. Begin met read-only controles.
5. Herhaal de oorspronkelijke test na herstel.
6. Registreer ook mislukte of geblokkeerde pogingen.

## Webapp start niet

Controleer repositorylocatie, launcher en Python:

    Get-Location
    Test-Path .\Run-NetworkLab.ps1
    python --version
    Test-Path .\app\server.py

Als de launcher bestaat, voer die uit vanuit de repositoryroot. Lees de volledige terminaluitvoer. Verzin geen alternatieve entrypoint als de huidige README die niet ondersteunt.

## Poort 8501 is bezet

Bekijk eerst welk proces de poort gebruikt:

    Get-NetTCPConnection -LocalPort 8501 -State Listen -ErrorAction SilentlyContinue

Koppel het proces-ID aan een proces:

    Get-Process -Id <PID>

Vervang <PID> alleen door het werkelijk waargenomen proces-ID. Beëindig het proces niet voordat je weet welke toepassing het is. Als de repository een alternatieve poort ondersteunt, gebruik de gedocumenteerde optie.

## Webapp bereikbaar, maar gegevens ontbreken

- Controleer de terminaluitvoer van de server.
- Controleer of de relevante API-route bestaat in de huidige code.
- Controleer of de gebruikte VirtualBox-installatie gevonden wordt.
- Vergelijk de UI met de read-only uitvoer van de onderliggende inspectie.
- Noteer onderscheid tussen “geen gegevens”, “controle mislukt” en “component niet aanwezig”.

## VBoxManage niet gevonden

    $VBoxManage = 'C:\Program Files\Oracle\VirtualBox\VBoxManage.exe'
    Test-Path $VBoxManage
    if (Test-Path $VBoxManage) { & $VBoxManage --version }

Als het pad niet bestaat, zoek via de geïnstalleerde VirtualBox-app of de Windows-installatiegegevens. Wijzig PATH niet blind en gebruik geen onbekend uitvoerbaar bestand.

## Host-only adapter of DHCP ontbreekt

    & $VBoxManage list hostonlyifs
    & $VBoxManage list dhcpservers
    & $VBoxManage list vms

Controleer naam, IPv4-adres, subnet, DHCP-pool en VM-adapter. Verwijder geen adapters om een duplicaat op te lossen voordat je hebt vastgesteld welke adapter bij NetworkLab hoort.

## VM krijgt geen DHCP-adres

In de gastconsole:

    ip -brief address
    ip route

Controleer vervolgens de VirtualBox-adaptermodus, de kabelstatus en DHCP-configuratie. Noteer de fout; vul niet zelf een willekeurig IP-adres in. Voer geen statische configuratie uit zonder dat dit in de labopdracht is afgesproken.

## Ping mislukt

Een mislukte ping bewijst niet automatisch dat de VM uitstaat. Controleer:
- of de VM actief is en een IP-adres heeft;
- of bron en doel in het bedoelde subnet zitten;
- of de route correct is;
- of ICMP door de gastfirewall wordt geblokkeerd;
- of een toepasselijke TCP-service een alternatieve test kan bieden.

Schakel een firewall niet standaard uit.

## Git synchronisatieprobleem

    git status --short --branch
    git remote -v

Bewaar lokale wijzigingen voordat je opnieuw synchroniseert. Gebruik geen reset --hard of force push als standaardoplossing.

## Wanneer escaleren

Stop en documenteer de situatie als de scope onduidelijk is, een actie data kan verwijderen, een fysieke interface geraakt kan worden, of de fout alleen te reproduceren is door beveiliging uit te schakelen.
