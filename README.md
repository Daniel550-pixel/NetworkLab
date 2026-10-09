# NetworkLab

## Stage Project — Network & Infrastructure Management

NetworkLab is a controlled, reproducible local laboratory for demonstrating:

1. **Installatie en configuratie van netwerk- en infrastructuuronderdelen**
2. **Beheer en monitoring van netwerk- en infrastructuuronderdelen**

## Technology Stack

| Technology | Purpose |
|---|---|
| GitHub | Version control, implementation, documentation and evidence |
| Python | Local HTTP server, monitoring, diagnostics and reporting |
| HTML/CSS/JavaScript | Localhost web application and laboratory UI |
| PowerShell | Network inspection, configuration safeguards and diagnostics |
| JSON | Lab configuration and evidence format |
| GitHub Actions | Automated validation |

## Local Web Application

The NetworkLab interface is now a **pure localhost web application**.

- No Streamlit runtime is required.
- No external frontend CDN or remote UI service is required.
- The Python standard library provides the local HTTP server.
- The browser connects only to `127.0.0.1`.
- Network telemetry is exposed through local `/api/*` endpoints.
- The UI is served from the repository's `web/` directory.

### Start

From the repository root in PowerShell:

```powershell
.\Run-NetworkLab.ps1
```

Then open:

```
http://127.0.0.1:8501
```

Optional custom port:

```powershell
.\Run-NetworkLab.ps1 -Port 8510
```

The launcher starts `app/server.py`, which serves the frontend and local telemetry API.

## Web Application Sections

- Command Center
- Topology
- Interfaces
- Addressing
- Connectivity
- Services
- Diagnostics
- Evidence
- VM storage & OS media

The topology visualization is rendered with native SVG. There are no external JavaScript dependencies.

## Safety Model

Network-changing operations remain disabled by default in `config/lab-config.json`. The baseline configuration workflow refuses to run unless the laboratory safety controls are explicitly enabled and an interface is supplied.

No production-network assumptions are encoded in the repository.

## Network Topology and VM Installation Documentation

The documented host-only topology, IPv4 addressing plan, component roles and pending connectivity tests are available in [`docs/network-topology.html`](docs/network-topology.html). The page uses inline HTML/CSS/SVG and does not require an external library or CDN. Addresses for the guest VMs remain marked as pending until they are read from the running guests and verified by connectivity tests. The step-by-step Ubuntu Server installation, DHCP validation, host/guest and guest/guest connectivity checks, and evidence checklist are in [`docs/vm-installation-guide.md`](docs/vm-installation-guide.md).

## Execution Order

1. Initialize and validate the environment.
2. Start the local NetworkLab web application.
3. Inspect the current network state.
4. Define and document the actual stage-lab topology.
5. Enable guarded configuration only when that topology is known.
6. Validate network and infrastructure state.
7. Run monitoring and reporting.
8. Preserve results as stage evidence.

## Status

**Localhost web application: IMPLEMENTED**

**VirtualBox VM infrastructure: IMPLEMENTED**

- NetworkLab-Lab host-only network
- Three role-based lab VMs
- 20 GB VDI storage per VM
- Explicit local ISO attachment/ejection
- DVD-first boot preparation for OS installation
- No automatic OS downloads or external media selection

The web layer is now independent of Streamlit and runs as a local Python HTTP application on `127.0.0.1`.
