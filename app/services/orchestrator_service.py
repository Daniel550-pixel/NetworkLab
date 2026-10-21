from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.services.architecture_service import get_architecture_state
from app.services.connectivity_service import get_connectivity_state
from app.services.evidence_service import get_evidence
from app.services.health_service import get_health
from app.services.readiness_service import get_lab_readiness
from app.services.virtualbox_telemetry_service import get_telemetry

def run_audit() -> dict[str, Any]:
    started = datetime.now(timezone.utc).isoformat()
    health = get_health()
    readiness = get_lab_readiness()
    telemetry = get_telemetry()
    connectivity = get_connectivity_state()
    architecture = get_architecture_state()
    evidence = get_evidence()

    gates = {
        "host_health": bool(health.get("connectivity_ok")) and bool(health.get("services_ok")),
        "vm_readiness": bool(readiness.get("ready")),
        "virtualbox_telemetry": bool(telemetry.get("healthy")),
        "connectivity": bool(connectivity.get("reachable")),
        "architecture": bool(architecture.get("layers")),
        "evidence": isinstance(evidence, dict),
    }

    return {
        "started_at": started,
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "mode": "read-only-audit",
        "ready": all(gates.values()),
        "gates": gates,
        "architecture": architecture,
        "connectivity": connectivity,
        "readiness": readiness,
        "telemetry": telemetry,
        "health": health,
        "evidence": evidence,
    }
