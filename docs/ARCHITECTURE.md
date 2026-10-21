# NetworkLab Architecture

## Control flow

NetworkLab follows:

**discover -> observe -> classify -> policy-check -> execute-safe-action -> verify -> persist-evidence -> report**

## Layers

1. Control Plane — local HTTP API and web UI.
2. Virtualization — VirtualBox network and VM lifecycle services.
3. Network — host-only lab network and read-only connectivity verification.
4. Runtime — VM topology, storage, ISO/media and runtime readiness.
5. Observability — health, telemetry, process state and Windows event correlation.
6. Recovery — issue engine with bounded autonomous remediation.
7. Verification — readiness and connectivity gates.
8. Evidence — persistent incident history and reproducible stage evidence.

## Safety boundary

The system may automatically repair VirtualBox host state only when the action is classified as safe and no lab VM is running.

The recovery engine must not:
- delete VM configuration;
- delete VDI files;
- delete lock files blindly;
- modify production networking;
- terminate running VM processes;
- reboot Windows automatically.

Unknown or unsafe failures are diagnosed and escalated.

## Stage separation

NetworkLab remains software-only and isolated from production networking. VirtualBox uses the dedicated NetworkLab-Lab host-only network.

## Operational state

The /api/architecture endpoint provides a consolidated architecture snapshot. /api/connectivity provides read-only reachability validation.
