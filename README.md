# NetworkLab

## Stage Project — Network & Infrastructure Management

NetworkLab is a controlled, reproducible lab environment for demonstrating:

1. **Installeert en configureert netwerk- en infrastructuuronderdelen**
2. **Beheert en monitort netwerk- en infrastructuuronderdelen**

## Technology Stack

| Technology | Purpose |
|---|---|
| GitHub | Version control, implementation, documentation and evidence |
| PowerShell | Installation checks, configuration, administration and diagnostics |
| Python | Monitoring, diagnostics and reporting |
| JSON | Lab configuration and safety controls |
| GitHub Actions | Automated syntax and runtime validation |

## Current implementation

- Environment prerequisite validation
- Network adapter and IP configuration inspection
- Guarded baseline configuration workflow
- Infrastructure service and process inspection
- Consolidated health and diagnostic checks
- Python configuration-driven monitoring
- JSON monitoring/report generation
- Connectivity, network and infrastructure validation tests
- Reproducible runbook
- Automated GitHub validation pipeline
- Stage evidence framework

## Safety model

Network-changing operations are disabled by default in `config/lab-config.json`. The baseline configuration script refuses to run unless the lab-scope safety controls are enabled and an explicit interface is supplied.

No production-network assumptions are encoded in the repository.

## Repository Structure

```text
NetworkLab/
├── .github/workflows/validate.yml
├── README.md
├── config/lab-config.json
├── docs/
├── logs/
├── powershell/
├── python/
└── tests/
```

## Execution order

1. Initialize and validate the environment.
2. Inspect the current network state.
3. Define and document the actual stage-lab topology.
4. Enable guarded configuration only when that topology is known.
5. Validate network and infrastructure state.
6. Run monitoring and reporting.
7. Preserve results as stage evidence.

## Status

**Implementation baseline: COMPLETE**

The repository now contains the executable baseline for installation checks, configuration safeguards, management, monitoring, diagnostics, testing, reporting and evidence. The remaining environment-specific work is to apply it to the actual stage-lab topology and record the observed results.
