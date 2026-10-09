# Monitoring en diagnostiek

## Doel

Monitoring verzamelt waargenomen netwerk- en systeeminformatie zodat de beheerder de toestand kan beoordelen en resultaten kan vastleggen. Een melding of gesimuleerde incidentstatus is niet hetzelfde als een bevestigde netwerkstoring.

## Te controleren onderdelen

| Onderdeel | Waarneming | Voorbeeldcontrole |
|---|---|---|
| Netwerkinterfaces | Naam, status, IPv4-configuratie | Get-NetAdapter, Get-NetIPConfiguration |
| IP-configuratie | Adres, prefix, gateway, DNS | Get-NetIPConfiguration |
| Connectiviteit | Bereikbaarheid van expliciet doel | Test-Connection of passende TCP-test |
| Services | Status van relevante Windows-services | Projectscript voor service-inspectie |
| Processen | Processen en resources | Projectscript voor procesinspectie |
| VirtualBox | VM's, host-only adapters, DHCP | VBoxManage list vms/hostonlyifs/dhcpservers |
| Gast-OS | Hostname, IP-adres, route | hostname, ip -brief address, ip route |
| Applicatie | Serverrespons en UI/API | Browser en lokale endpoint-controle |

## Uitvoeren

Voer vanuit de repositoryroot uit, nadat je hebt gecontroleerd dat de bestanden bestaan:

    ./powershell/diagnostics/Test-NetworkLabConfiguration.ps1
    ./powershell/diagnostics/Invoke-NetworkLabDiagnostics.ps1
    ./powershell/manage/Get-NetworkLabHealth.ps1
    python ./python/monitoring/run_monitor.py

## Werkwijze bij afwijkingen

1. Noteer tijdstip, component en verwachte toestand.
2. Herhaal de observatie om een tijdelijke fout uit te sluiten.
3. Controleer interface- en adresconfiguratie.
4. Test een tweede relevante laag, bijvoorbeeld een TCP-service als ICMP geblokkeerd is.
5. Vergelijk met de laatst bekende goede toestand.
6. Noteer de oorzaak alleen als waarnemingen die ondersteunen; anders noteer je “oorzaak onbekend”.
7. Voer na herstel dezelfde test opnieuw uit.

## Teststatussen

- **Geslaagd:** de waargenomen toestand voldoet aan het vooraf vastgelegde criterium.
- **Mislukt:** de waargenomen toestand voldoet niet aan het criterium.
- **Geblokkeerd:** de test kon niet veilig of technisch worden uitgevoerd.
- **Niet uitgevoerd:** er is nog geen meting gedaan.

Gebruik “openstaand” of “niet gemeten” zolang er geen werkelijke uitvoer is. Vul geen fictieve resultaten of IP-adressen in.

## Rapportage

Een bruikbaar rapport bevat datum/tijd, omgeving, script/commando, component, verwacht resultaat, werkelijk resultaat, status, foutmelding, log- of screenshotreferentie, conclusie en vervolgactie.

De monitoring- en rapportagescripts staan onder python/monitoring/, python/diagnostics/ en python/reporting/. Zie [Stage-bewijs](evidence.md) en [Testplan](test-plan.md).
