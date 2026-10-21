# Verificatieformulier — NetworkLab

Gebruik dit formulier tijdens een echte controle van de lokale labomgeving. Vul alleen waarden in die je zelf hebt waargenomen. Gebruik `Niet gecontroleerd` als iets nog niet is vastgesteld; vul geen voorbeeldwaarden in alsof ze echt zijn.

## Registratie

- **Datum en tijd:** [invullen]
- **Uitvoerder:** [invullen]
- **Git-branch en commit:** [invullen met `git branch --show-current` en `git rev-parse --short HEAD`]
- **Doel van de controle:** [invullen]
- **Gebruikte host:** [apparaatnaam/Windows-versie, indien relevant]

## 1. Windows-host en VirtualBox

| Controlepunt | Waargenomen waarde | Resultaat / opmerking |
|---|---|---|
| VirtualBox-versie | Niet gecontroleerd | |
| Host-only-adapternaam | Niet gecontroleerd | |
| Host IPv4-adres en prefix | Niet gecontroleerd | |
| Labnetwerknaam | Niet gecontroleerd | |
| DHCP ingeschakeld? | Niet gecontroleerd | |
| DHCP-bereik | Niet gecontroleerd | |

Commando's op de Windows-host:

```powershell
Get-NetIPConfiguration
Get-NetIPAddress -AddressFamily IPv4 |
    Sort-Object InterfaceAlias |
    Format-Table InterfaceAlias, IPAddress, PrefixLength
& "C:\Program Files\Oracle\VirtualBox\VBoxManage.exe" --version
& "C:\Program Files\Oracle\VirtualBox\VBoxManage.exe" list hostonlyifs
& "C:\Program Files\Oracle\VirtualBox\VBoxManage.exe" list vms
```

## 2. VM-inventaris en netwerkadapters

Vul één regel per aangetroffen VM in. Gebruik de exacte naam die VirtualBox teruggeeft.

| Exacte VM-naam | Status | Adaptertype / netwerknaam | MAC-adres | Gast-IP/prefix | Gateway | DNS |
|---|---|---|---|---|---|---|
| [VM 1] | Niet gecontroleerd | Niet gecontroleerd | Niet gecontroleerd | Niet gecontroleerd | Niet gecontroleerd | Niet gecontroleerd |
| [VM 2] | Niet gecontroleerd | Niet gecontroleerd | Niet gecontroleerd | Niet gecontroleerd | Niet gecontroleerd | Niet gecontroleerd |
| [VM 3] | Niet gecontroleerd | Niet gecontroleerd | Niet gecontroleerd | Niet gecontroleerd | Niet gecontroleerd | Niet gecontroleerd |

Inspecteer elke VM met de exacte naam:

```powershell
& "C:\Program Files\Oracle\VirtualBox\VBoxManage.exe" showvminfo "EXACTE-VM-NAAM"
```

Controleer de gastconfiguratie vanuit het gastbesturingssysteem. Windows: `ipconfig /all`. Linux: `ip address` en `ip route`; controleer DNS met de passende distributiecommando's.

## 3. Connectiviteit

| Bron | Bestemming | Methode / commando | Verwacht resultaat | Werkelijk resultaat |
|---|---|---|---|---|
| Windows-host | Host-only-adres | `ping <adres>` (indien toegestaan) | Vast te stellen | Niet gecontroleerd |
| VM 1 | VM 2 | `ping <adres>` (indien toegestaan) | Vast te stellen | Niet gecontroleerd |
| VM 2 | VM 3 | `ping <adres>` (indien toegestaan) | Vast te stellen | Niet gecontroleerd |
| VM naar DNS/service | Alleen indien ingericht | Passende naam- of poorttest | Vast te stellen | Niet gecontroleerd |

**Interpretatie:** een mislukte ping bewijst niet automatisch dat een netwerkverbinding defect is; de firewall kan ICMP blokkeren. Noteer daarom ook de route, adapterstatus en eventuele toepasselijke service- of poorttest.

## 4. Veiligheidscontrole

- [ ] De beoogde labadapter is ondubbelzinnig geïdentificeerd.
- [ ] Geen productieadapter is aangepast.
- [ ] De configuratie is vóór wijziging vastgelegd.
- [ ] Wijzigingen zijn beperkt tot het bedoelde lab.
- [ ] Na afloop zijn de netwerkstatus en VM-status opnieuw gecontroleerd.
- [ ] Gevoelige gegevens, tokens, wachtwoorden en publieke IP-informatie zijn uit screenshots/logs verwijderd.

## 5. Bewijsstukken

| Bewijs-ID | Bestand / screenshot | Welke controle toont het? | Resultaat |
|---|---|---|---|
| E-01 | [bestandsnaam] | [controle] | [geslaagd / afwijking] |
| E-02 | [bestandsnaam] | [controle] | [geslaagd / afwijking] |
| E-03 | [bestandsnaam] | [controle] | [geslaagd / afwijking] |

Bewaar bij voorkeur screenshots en opgeschoonde uitvoer in een aparte bewijsmap. Commit geen tijdelijke logs of gevoelige hostgegevens zonder noodzaak.

## 6. Afwijkingen en herstel

Voor iedere afwijking:

1. **Waarneming:** wat ging niet volgens verwachting?
2. **Impact:** welke VM, adapter, service of opdracht werd geraakt?
3. **Oorzaak:** welke controle ondersteunt de vermoedelijke oorzaak?
4. **Herstel:** welke wijziging is uitgevoerd?
5. **Hertest:** welk commando of welke handeling bevestigde het resultaat?
6. **Rest-risico:** wat is nog niet opgelost of geverifieerd?

## 7. Conclusie

- **Eindresultaat:** [geslaagd / gedeeltelijk geslaagd / niet geslaagd]
- **Wat is daadwerkelijk geverifieerd:** [invullen]
- **Wat is gesimuleerd of alleen gedocumenteerd:** [invullen]
- **Openstaande acties:** [invullen]
- **Reflectie / volgende verbetering:** [invullen]

> Dit formulier is een registratiehulpmiddel en geen vervanging voor het officiële beoordelingsformulier van school of stagebedrijf. Maak expliciet onderscheid tussen werkelijk uitgevoerde controles, simulaties en nog niet geverifieerde aannames.
