# Stage Evidence

This document maps the implementation to the two required stage competencies.

## Competency 1

**Installeert en configureert netwerk- en infrastructuuronderdelen**

### Evidence available

- `powershell/install/Initialize-NetworkLab.ps1` — validates the lab execution environment without changing the host.
- `powershell/configure/Get-NetworkConfiguration.ps1` — captures adapter, IPv4, gateway and DNS state.
- `powershell/configure/Set-NetworkLabBaseline.ps1` — guarded configuration workflow requiring explicit lab scope and interface selection.
- `powershell/diagnostics/Test-NetworkLabConfiguration.ps1` — validates adapter, IPv4 and gateway state.
- `tests/network/Test-NetworkConfiguration.ps1` — executable network-state validation.

### Required recorded evidence

For the actual stage lab, record the topology, interface used, intended configuration, command executed, expected state, observed state and validation result.

## Competency 2

**Beheert en monitort netwerk- en infrastructuuronderdelen**

### Evidence available

- `powershell/manage/Get-NetworkLabServices.ps1` — service inspection.
- `powershell/manage/Get-NetworkLabProcesses.ps1` — process/resource inspection.
- `powershell/manage/Get-NetworkLabHealth.ps1` — consolidated infrastructure health check.
- `powershell/diagnostics/Invoke-NetworkLabDiagnostics.ps1` — consolidated diagnostics.
- `python/monitoring/run_monitor.py` — configuration-driven monitoring.
- `python/monitoring/system_monitor.py` — system-state collection.
- `python/diagnostics/network_diagnostics.py` — TCP diagnostics.
- `python/reporting/generate_report.py` — monitoring result reporting.
- `python/reporting/write_report.py` — timestamped evidence report output.
- `tests/connectivity/Test-Connectivity.ps1` — connectivity validation.
- `tests/infrastructure/Test-Infrastructure.ps1` — infrastructure-service validation.

## Network topology diagram

- [`docs/network-topology.html`](network-topology.html) — HTML/SVG topology diagram showing the Windows host, local web application, VirtualBox host-only adapter, DHCP server and three role-based VMs.
- The diagram records configured addressing (`192.168.77.0/24`, host `192.168.77.1`, DHCP server `192.168.77.2`, pool `192.168.77.100–192.168.77.200`).
- VM IP addresses and end-to-end connectivity are explicitly marked as pending until measured. The diagram is a documentation artefact, not proof that the guest operating systems are installed or reachable.

## VM installation and connectivity evidence

Follow [`vm-installation-guide.md`](vm-installation-guide.md) to install Ubuntu Server on the three VirtualBox guests and record observed DHCP addresses and connectivity results. The guide's registration table starts as **Openstaand**; update it only after performing the tests and saving the actual output/screenshots. Do not treat the planned topology as proof of working connectivity.

## Evidence standard

Each recorded evidence item should identify:

- objective
- environment
- topology/component
- procedure
- command or script used
- expected result
- actual result
- conclusion
- timestamp
- supporting log or screenshot when appropriate

## Validation

GitHub Actions validates Python compilation/execution and PowerShell syntax on pushes and pull requests to `main`.
