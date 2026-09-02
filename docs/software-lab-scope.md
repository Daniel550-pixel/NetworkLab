# Software-only Stage Lab Scope

## Purpose

NetworkLab is implemented as a software-only lab for demonstrating the two known stage competencies:

- **Installeert en configureert netwerk- en infrastructuuronderdelen**
- **Beheert en monitort netwerk- en infrastructuuronderdelen**

## Explicit scope

- No physical routers or switches are required.
- No physical cabling is required.
- No production-network configuration is encoded.
- Network state is inspected through Windows networking interfaces and PowerShell.
- Infrastructure state is represented by operating-system services and processes.
- Python provides portable monitoring and reporting.
- GitHub provides versioning and evidence traceability.

## Configuration rule

The repository does not contain an assumed IP plan, VLAN plan, gateway plan, or interface mapping because those details were not specified in the available assignment information.

`config/lab-config.json` therefore keeps interface-specific configuration empty and keeps configuration changes disabled by default.

## Demonstration flow

1. Run `powershell/install/Initialize-NetworkLab.ps1` to validate prerequisites.
2. Run `powershell/configure/Get-NetworkLabState.ps1` to inspect network state.
3. Run `powershell/diagnostics/Invoke-NetworkLabHealthCheck.ps1` for the consolidated health check.
4. Run `powershell/manage/Get-NetworkLabEvidence.ps1` to generate evidence data.
5. Run `python python/monitoring/run_monitor.py` for the Python monitoring cycle.
6. Run `python python/reporting/generate_report.py` with monitoring JSON when a report is required.

Any later assignment-specific topology can be added without changing the safety model.
