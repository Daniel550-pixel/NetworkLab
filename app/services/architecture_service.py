from __future__ import annotations

from typing import Any

from app.services.readiness_service import get_lab_readiness
from app.services.virtualbox_telemetry_service import get_telemetry
from app.services.virtualization_service import get_virtual_network
from app.services.vm_service import get_vm_topology

ARCHITECTURE_LAYERS = [
    {"id": "control", "name": "Control Plane", "purpose": "Single local orchestration surface for lab state, lifecycle and diagnostics."},
    {"id": "virtualization", "name": "Virtualization", "purpose": "VirtualBox network and VM lifecycle abstraction."},
    {"id": "network", "name": "Network", "purpose": "Host-only lab network, addressing and connectivity validation."},
    {"id": "runtime", "name": "Runtime", "purpose": "VM topology, storage, media and runtime readiness."},
    {"id": "observability", "name": "Observability", "purpose": "Health, telemetry, incidents, evidence and persistent event history."},
    {"id": "recovery", "name": "Recovery", "purpose": "Issue classification, safe autonomous remediation and escalation."},
    {"id": "verification", "name": "Verification", "purpose": "Readiness and connectivity checks before declaring the lab operational."},
    {"id": "evidence", "name": "Evidence", "purpose": "Reproducible state and test evidence for the stage project."},
]

def _status(ok: bool) -> str:
    return "ready" if ok else "attention"

def get_architecture_state() -> dict[str, Any]:
    readiness = get_lab_readiness()
    telemetry = get_telemetry()
    network = get_virtual_network()
    topology = get_vm_topology()
    network_ready = bool(network.get("ready")) if isinstance(network, dict) else False
    topology_ready = bool(topology.get("available")) if isinstance(topology, dict) else False
    telemetry_ready = bool(telemetry.get("healthy"))
    readiness_ready = bool(readiness.get("ready"))
    return {
        "project": "NetworkLab",
        "mode": "stage-lab",
        "principle": "observe -> decide -> safely execute -> verify -> record",
        "layers": [
            {**ARCHITECTURE_LAYERS[0], "status": "ready"},
            {**ARCHITECTURE_LAYERS[1], "status": _status(network_ready)},
            {**ARCHITECTURE_LAYERS[2], "status": _status(network_ready)},
            {**ARCHITECTURE_LAYERS[3], "status": _status(topology_ready)},
            {**ARCHITECTURE_LAYERS[4], "status": _status(telemetry_ready)},
            {**ARCHITECTURE_LAYERS[5], "status": _status(telemetry_ready)},
            {**ARCHITECTURE_LAYERS[6], "status": _status(readiness_ready)},
            {**ARCHITECTURE_LAYERS[7], "status": "ready"},
        ],
        "pipeline": [
            "discover", "observe", "classify", "policy-check",
            "execute-safe-action", "verify", "persist-evidence", "report",
        ],
        "network": network,
        "topology": topology,
        "readiness": readiness,
        "telemetry": {
            "status": telemetry.get("status"),
            "healthy": telemetry.get("healthy"),
            "active_issue": telemetry.get("active_issue"),
            "repair_count": telemetry.get("repair_count"),
        },
    }
