# Incident simulation and monitoring

## Purpose

This module demonstrates a controlled incident lifecycle for the NetworkLab stage project. It is a **simulation only**: it changes a local JSON state file and writes local JSON Lines (JSONL) events. It does not disconnect a real network interface or interrupt production services.

## Components

| Component | Responsibility |
|---|---|
| `config/simulation/incident-state.json` | Stores the current simulated incident state |
| `config/simulation/monitoring-cursor.json` | Runtime cursor used by the feed to remember the last observed status; created automatically |
| `tests/incidents/Invoke-NetworkLabIncidentSimulation.ps1` | Advances the incident through lifecycle actions |
| `tests/incidents/Test-NetworkLabIncidentSimulation.ps1` | Automated integration test for lifecycle order, event logging, monitoring detection, recovery, and invalid action order |
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

The lifecycle script validates the required state before every action. An action that is called out of sequence stops with an error.

## Monitoring feed

Start the feed with the default 30-second polling interval:

```powershell
.\powershell\manage\Start-NetworkLabMonitoringFeed.ps1
```

For a bounded test run, use a one-second interval and one iteration:

```powershell
.\powershell\manage\Start-NetworkLabMonitoringFeed.ps1 -IntervalSeconds 1 -Iterations 1
```

The feed writes a detection event when it observes `fault_injected` after a different previous state. It stores its last observed status in `config/simulation/monitoring-cursor.json`; reset that runtime cursor only when you intentionally want to reset the feed's detection history. It is a file-based demonstration, not a live network probe. It does not independently detect packet loss, interface failure, or other real network conditions, and it does not emit an event for every lifecycle state transition.

With the default `-Iterations 0`, the feed continues until stopped with **Ctrl+C**. Use a positive iteration count for a bounded run.

## Automated validation

The GitHub Actions workflow validates Python syntax, runs the infrastructure unit tests, executes the read-only monitoring runner and report generator, validates PowerShell syntax, and runs the incident simulation integration test. Check the [NetworkLab Validation workflow](https://github.com/Daniel550-pixel/NetworkLab/actions/workflows/validate.yml) for the result associated with the latest commit.

The incident integration test temporarily backs up the state, cursor, and related logs, runs the lifecycle and monitoring flow, asserts expected events and final state, and restores the original files in a `finally` block. This protects pre-existing local test data if the test exits normally or throws an error.

Manual verification was also performed locally on 9 October 2026. That manual run is separate from the automated CI result; neither simulation proves that real network connectivity monitoring or recovery is implemented.

## Remaining test coverage

- Add tests for malformed and missing state files.
- Add dedicated monitoring tests for missing state, malformed cursor, normal state, and repeated polling.
- Consider whether monitoring should detect additional state transitions and avoid duplicate events.
- Keep simulation logs separate from real infrastructure telemetry.

## Relevance to the stage assignment

This module provides evidence for documenting a controlled infrastructure scenario, executing a defined procedure, observing state changes, recording results, and identifying improvements. Map these activities to the exact assessment indicators for **B1-K2-W1/W2** used by the school or internship provider; this page does not replace the official assessment rubric.
