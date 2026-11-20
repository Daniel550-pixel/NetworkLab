# NetworkLab — projectstructuur

Verplaats bestaande bestanden niet zonder eerst de launcher-, taakplanner- en importscripts bij te werken.

## Hoofdmappen

| Pad | Inhoud |
|---|---|
| `apps/client/` | Client UI, poort 8510 |
| `apps/mgmt/` | Management UI, poort 8511 |
| `apps/infra/` | Infrastructure UI en API, poort 8512 |
| `config/` | Niet-geheime labconfiguratie |
| `docs/` | Architectuur, installatie, runbook, testplan en HTML-documentatie |
| `evidence/` | Bewijsbestanden; runtime-JSON blijft standaard lokaal |
| `logs/` | Lokale uitvoer- en herstellogs |
| `powershell/configure/` | Configuratie- en inventarisatiescripts |
| `powershell/diagnostics/` | Health checks, tests, herstelbewaking en netwerktekening |
| `powershell/install/` | Installatie- en initialisatiescripts |
| `powershell/manage/` | Status, processen en bewijs uitlezen |
| `powershell/maintenance/` | Git-synchronisatie en onderhoud |
| `tests/` | Python- en PowerShell-tests |
| `.github/workflows/` | GitHub Actions-validatie |

## Belangrijke scripts

- `Run-NetworkLab-WebApps.ps1`: start de drie webapps.
- `powershell/diagnostics/Run-NetworkLabAutoRecovery.ps1`: supervisor.
- `powershell/diagnostics/Ensure-NetworkLabWebApps.ps1`: herstelt webapps.
- `powershell/diagnostics/Test-NetworkLabWebApps.ps1`: test drie UI's en twee API-routes.
- `powershell/diagnostics/New-NetworkLabPixelDiagram.ps1`: genereert de PNG-netwerktekening.
- `docs/networklab-pixel-netwerktekening.html`: HTML/SVG-netwerktekening.
- `powershell/maintenance/Sync-NetworkLabToGitHub.ps1`: veilige Git-synchronisatie.

## Git-regels

- Werk op `feature/three-webapps-no-vms` tenzij bewust anders afgesproken.
- Gebruik geen force-push.
- Push geen `.env`, credentials, private keys, caches of runtime-logbestanden.
- Deel runtime-bewijs alleen na controle op persoonsgegevens, lokale paden en gevoelige gegevens.
- Een commit is geen vervanging voor daadwerkelijk uitgevoerde tests.
