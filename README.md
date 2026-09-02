# NetworkLab

## Stage Project — Network & Infrastructure Management

NetworkLab is a controlled, reproducible lab environment for demonstrating the following stage competencies:

1. **Installeert en configureert netwerk- en infrastructuuronderdelen**
2. **Beheert en monitort netwerk- en infrastructuuronderdelen**

The repository contains the configuration, management, diagnostics, monitoring, testing and documentation required to demonstrate these competencies.

## Project Goals

- Configure network and infrastructure components in a controlled lab environment.
- Automate repeatable administration tasks with PowerShell.
- Monitor network and system state with Python.
- Perform connectivity and infrastructure diagnostics.
- Record test results and operational evidence.
- Keep every procedure reproducible from the repository.

## Technology Stack

| Technology | Purpose |
|---|---|
| GitHub | Version control, source code, documentation and stage evidence |
| PowerShell | Installation, configuration, administration and diagnostics |
| Python | Monitoring, analysis and reporting |
| JSON | Lab configuration and monitoring parameters |

## Repository Structure

```text
NetworkLab/
├── README.md
├── powershell/
│   ├── install/
│   ├── configure/
│   ├── manage/
│   └── diagnostics/
├── python/
│   ├── monitoring/
│   ├── diagnostics/
│   └── reporting/
├── config/
│   └── lab-config.json
├── tests/
│   ├── connectivity/
│   ├── network/
│   └── infrastructure/
├── logs/
│   └── .gitkeep
└── docs/
    ├── installation.md
    ├── configuration.md
    ├── management.md
    ├── monitoring.md
    └── evidence.md
```

## Architecture

```text
                    NetworkLab
                        │
             ┌──────────┴──────────┐
             │                     │
       CONFIGURATION           MONITORING
             │                     │
        PowerShell               Python
             │                     │
      ┌──────┴──────┐       ┌──────┴──────┐
      │             │       │             │
   Network     Infrastructure Network     System
      │             │       │             │
      └──────┬──────┘       └──────┬──────┘
             │                     │
             └──────────┬──────────┘
                        │
                   DIAGNOSTICS
                        │
                     LOGGING
                        │
                     GITHUB
                        │
                  STAGE-BEWIJS
```

## Design Principles

### 1. Reproducibility
Every important operation should be executable from a documented procedure or script.

### 2. Safety
Network-changing operations must be explicitly scoped to the lab environment. Read-only diagnostics and monitoring are preferred during development.

### 3. Separation of responsibilities

- **PowerShell** handles administration and configuration.
- **Python** handles monitoring, analysis and reporting.
- **GitHub** stores the implementation and evidence trail.

### 4. Evidence-driven development
Each completed capability should produce a verifiable result that can be used as stage evidence.

### 5. Minimal scope
This repository is specifically for the stage assignments. Unrelated AIOS, ULTRON, hobby automation and experimental systems do not belong here.

## Development Order

1. Repository foundation
2. Lab configuration
3. PowerShell configuration and administration layer
4. Python monitoring layer
5. Diagnostics
6. Automated tests
7. Logging and reporting
8. Stage evidence documentation
9. Validation and cleanup

## Status

**Phase 1 — Repository Foundation: COMPLETE**

The repository foundation is established. Functional PowerShell and Python components will be added incrementally and validated before being used as stage evidence.
