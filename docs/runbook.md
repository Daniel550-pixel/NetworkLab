# NetworkLab Runbook

## 1. Initialize

Run from PowerShell in the repository root:

```powershell
./powershell/install/Initialize-NetworkLab.ps1
```

The command verifies the Windows networking cmdlets and reports Python availability. It does not modify the system.

## 2. Inspect configuration

```powershell
./powershell/configure/Get-NetworkLabState.ps1
./powershell/configure/Get-NetworkConfiguration.ps1
```

## 3. Validate the current network

```powershell
./powershell/diagnostics/Test-NetworkLabConfiguration.ps1
./tests/network/Test-NetworkConfiguration.ps1
./tests/connectivity/Test-Connectivity.ps1
```

## 4. Inspect infrastructure

```powershell
./powershell/manage/Get-NetworkLabServices.ps1
./powershell/manage/Get-NetworkLabProcesses.ps1
./powershell/manage/Get-NetworkLabHealth.ps1
```

## 5. Run Python monitoring

```powershell
python ./python/monitoring/run_monitor.py
```

## 6. Generate a report

```powershell
'[]' | python ./python/reporting/generate_report.py
```

## 7. Configuration changes

`Set-NetworkLabBaseline.ps1` is guarded by the lab configuration safety switch and requires an explicit interface. Do not enable configuration changes until the actual stage-lab topology, IP plan and DNS plan have been documented.
