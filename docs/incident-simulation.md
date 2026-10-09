# Incident simulation and monitoring

## Purpose

This module demonstrates a controlled incident lifecycle for the NetworkLab stage project. It is a **simulation only**: it changes a local JSON state file and writes local JSON Lines (JSONL) events. It does not disconnect a real network interface or interrupt production services.

## Components

| Component | Responsibility |
|---|---|
| `config/simulation/incident-state.json` | Stores the current simulated incident state |
| `tests/incidents/Invoke-NetworkLabIncidentSimulation.ps1` | Advances the incident through lifecycle actions |
| `powershell/manage/Start-NetworkLabMonitoringFeed.ps1` | Polls the state file and detects a transition to `fault_injected` |
| `logs/incident-simulation.jsonl` | Records lifecycle actions |
| `logs/monitoring-detection.jsonl` | Records detections emitted by the monitoring feed |
| `logs/monitoring-feed.log` | Human-readable runtime messages from the monitoring feed |

## Incident lifecycle

The simulation supports these actions, in this order:

1. `InjectFault`: changes the state from `normal` to `fault_injected` and records `FAULT_INJECTED`.
2. `Detect`: requires `fault_injected`, changes the state to `detected`, and records `DETECTED`.
3. `Recover`: requires `detected`, changes the state to `recovery`, and records `RECOVERY`.
4. `Verify`: requires `recovery`, records `VERIFIED`, and returns the stored state to `normal`.

Run each action from the repository root in PowerShell:

```powershell
.\tests\incidents\Invoke-NetworkLabIncidentSimulation.ps1 -Action InjectFault
.\tests\incidents\Invoke-NetworkLabIncidentSimulation.ps1 -Action Detect
.\tests\incidents\Invoke-NetworkLabIncidentSimulation.ps1 -Action Recover
.\tests\incidents\Invoke-NetworkLabIncidentSimulation.ps1 -Action Verify
```

The lifecycle script validates the required state before `Detect`, `Recover`, and `Verify`. An action that is called out of sequence stops with an error.

## Monitoring feed

Start the feed with the default 30-second polling interval:

```powershell
.\powershell\manage\Start-NetworkLabMonitoringFeed.ps1
```

For a bounded test run, use a one-second interval and one iteration:

```powershell
.\powershell\manage\Start-NetworkLabMonitoringFeed.ps1 -IntervalSeconds 1 -Iterations 1
```

The feed writes a detection event when it observes `fault_injected` after a different previous state. It is a file-based demonstration, not a live network probe. It currently does not independently detect packet loss, interface failure, or other real network conditions. It also does not emit a detection event for every possible lifecycle state transition.

Stop an unbounded run with **Ctrl+C**.

## Verification evidence

Manual PowerShell verification was completed on 9 October 2026:

- The four lifecycle actions completed in order.
- The stored state matched each expected intermediate state and returned to `normal` after `Verify`.
- The expected lifecycle event types were found in `incident-simulation.jsonl`.
- The monitoring feed observed `fault_injected` and wrote a `DETECTED` JSONL event with `simulation: true`, scenario `connectivity-loss`, and target `simulated-network-node`.
- The checks used backups and restored the original state and log files after the tests.

These are manual test results from the local environment, not evidence of an automated CI test suite.

## Limitations and next improvements

- Add automated tests for invalid action order and malformed/missing state files.
- Add dedicated tests for the monitoring feed, including normal state, incident transition, and repeated polling.
- Consider whether monitoring should detect additional state transitions and avoid duplicate events.
- Keep simulation logs separate from real infrastructure telemetry.
- Do not use this simulation as proof that real connectivity monitoring or recovery has been implemented.

## Relevance to the stage assignment

This module provides evidence for documenting a controlled infrastructure scenario, executing a defined procedure, observing state changes, recording results, and identifying improvements. Map these activities to the exact assessment indicators for **B1-K2-W1/W2** used by the school or internship provider; this page does not replace the official assessment rubric.
