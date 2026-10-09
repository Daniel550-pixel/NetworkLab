# VM-installatiehandleiding — NetworkLab

## Doel

Deze handleiding beschrijft hoe de drie NetworkLab-gastmachines met Ubuntu Server worden geïnstalleerd en daarna gecontroleerd. Voer de stappen uit op de Windows-host met VirtualBox 7.2.6.

> **Status:** dit is een uitvoeringshandleiding. Markeer een stap pas als afgerond nadat je het resultaat zelf hebt waargenomen en bewijs hebt opgeslagen.

## 1. Voorcontrole op Windows

Open PowerShell en voer uit:

```powershell
$VBoxManage = "C:\Program Files\Oracle\VirtualBox\VBoxManage.exe"
if (-not (Test-Path $VBoxManage)) { throw "VBoxManage.exe niet gevonden: $VBoxManage" }

& $VBoxManage list vms
& $VBoxManage list hostonlyifs
& $VBoxManage list dhcpservers
```

Controleer dat deze VM's bestaan:

- `NetworkLab-VM01-MGMT`
- `NetworkLab-VM02-INFRA`
- `NetworkLab-VM03-CLIENT`

Controleer voor alle drie dat netwerkadapter 1 is gekoppeld aan de bedoelde host-only adapter (Adapter #4) en dat de kabel is aangesloten. Verander geen fysieke netwerkadapter.

## 2. Installeer Ubuntu Server op VM01

ISO-bestand dat voor dit lab is vastgelegd:

`C:\Users\Daan Salden\Downloads\ubuntu-24.04.5-live-server-amd64.iso`

1. Zet alleen `NetworkLab-VM01-MGMT` aan via de VirtualBox-GUI.
2. Kies **Try or Install Ubuntu Server** en start de installatie.
3. Selecteer taal en toetsenbordindeling.
4. Gebruik de standaard Ubuntu Server-installatie.
5. Laat IPv4 op DHCP staan. Noteer eventuele netwerkfoutmeldingen; verzin geen IP-adres.
6. Laat de proxy leeg tenzij de stageomgeving expliciet een proxy vereist.
7. Selecteer de virtuele schijf van 20 GB als installatiedoel en bevestig dat alleen de virtuele schijf wordt gewijzigd.
8. Maak een eigen labgebruikersaccount aan. Gebruik geen echte wachtwoorden in de documentatie of screenshots.
9. Schakel **Install OpenSSH server** in als die optie beschikbaar is.
10. Voltooi de installatie en kies **Reboot**.
11. Als de VM opnieuw in de installer start, zet de VM uit en verwijder alleen de ISO uit de virtuele dvd-drive via **Settings → Storage**. Start daarna opnieuw op.

## 3. Controle in de Ubuntu-gast

Meld aan in de VM-console en voer uit:

```bash
hostname
ip -brief address
ip route
ping -c 3 192.168.77.1
```

Leg de werkelijke uitvoer vast. De VM hoort een IPv4-adres uit de ingestelde DHCP-pool `192.168.77.100–192.168.77.200` te ontvangen. Als er geen adres is, registreer dat als een mislukte test en onderzoek de DHCP-/adapterconfiguratie.

Voer vanaf Windows, met het werkelijk waargenomen IP-adres, uit:

```powershell
Test-Connection -ComputerName "<WERKELIJK_VM_IP>" -Count 4
```

Vervang de placeholder voordat je de opdracht uitvoert. Een mislukte ping alleen bewijst niet dat de VM uitstaat; controleer ook de VM-console en eventueel een relevante TCP-service.

## 4. Herhaal voor VM02 en VM03

Herhaal hoofdstuk 2 en 3 voor:

| VM | Rol | Hostnamevoorstel |
|---|---|---|
| `NetworkLab-VM02-INFRA` | Infrastructuurtests | `networklab-infra` |
| `NetworkLab-VM03-CLIENT` | Clienttests | `networklab-client` |

Gebruik per VM de eigen virtuele schijf. Controleer vóór de installatie dat je de juiste VM hebt geopend.

## 5. Test VM-naar-VM-connectiviteit

Nadat alle drie VM's zijn geïnstalleerd en hun IP-adressen zijn vastgelegd:

1. Noteer de drie IP-adressen en de tijd waarop ze zijn waargenomen.
2. Test vanaf VM01 de twee andere VM-adressen met `ping -c 3 <IP>`.
3. Herhaal ten minste één test in omgekeerde richting.
4. Noteer bron, bestemming, opdracht, verwachte uitkomst, werkelijk resultaat en eventuele foutmelding.
5. Als ICMP geblokkeerd is, controleer de firewall en test indien passend een echte TCP-service; schakel de firewall niet zomaar uit.

## 6. Bewijs vastleggen

Bewaar per VM minimaal:

- Screenshot van de VM-naam in VirtualBox.
- Screenshot van een succesvolle login/console na installatie.
- Uitvoer van `hostname`, `ip -brief address` en `ip route`.
- Resultaat van de host-naar-VM-test.
- Resultaat van de VM-naar-VM-test.
- Datum/tijd en conclusie.

Redigeer gebruikersnamen of andere gevoelige gegevens indien nodig. Bewaar geen wachtwoorden, tokens of private sleutels in Git.

## 7. Registratietabel

Vul pas in na uitvoering:

| Controle | Verwacht resultaat | Werkelijk resultaat | Status |
|---|---|---|---|
| VM01 Ubuntu start | OS start vanaf virtuele schijf | Nog niet gemeten | Openstaand |
| VM01 DHCP | IPv4 uit de DHCP-pool | Nog niet gemeten | Openstaand |
| VM02 Ubuntu + DHCP | OS start en krijgt IPv4 | Nog niet gemeten | Openstaand |
| VM03 Ubuntu + DHCP | OS start en krijgt IPv4 | Nog niet gemeten | Openstaand |
| Windows → VM01/02/03 | Bereikbaarheid aantoonbaar | Nog niet gemeten | Openstaand |
| VM01 ↔ VM02 | Communicatie aantoonbaar | Nog niet gemeten | Openstaand |
| VM02 ↔ VM03 | Communicatie aantoonbaar | Nog niet gemeten | Openstaand |

## Afbakening

Dit lab gebruikt een VirtualBox host-only netwerk en is bedoeld voor gecontroleerde tests. De aanwezigheid van deze handleiding of een topologietekening is geen bewijs dat een OS-installatie, DHCP-lease of verbinding succesvol is. Registreer alleen resultaten die daadwerkelijk zijn gemeten.
