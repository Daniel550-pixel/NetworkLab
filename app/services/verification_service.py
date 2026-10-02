from __future__ import annotations

from typing import Any

from app.services.connectivity_service import get_connectivity_state
from app.services.lab_lifecycle_service import get_lab_state
from app.services.virtualbox_telemetry_service import get_telemetry

def verify_lab() -> dict[str, Any]:
    state = get_lab_state()
    connectivity = get_connectivity_state()
    telemetry = get_telemetry()
    readiness = state["readiness"]

    checks = [
        {"id": "network", "label": "Virtual network", "passed": bool(state["network"].get("ready"))},
        {"id": "vm-topology", "label": "VM topology", "passed": all(vm.get("exists") and vm.get("network") == "NetworkLab-Lab" for vm in state["topology"].get("vms", []))},
        {"id": "storage", "label": "VM storage", "passed": all(vm.get("disk") for vm in state["storage"].get("vms", []))},
        {"id": "connectivity", "label": "Host connectivity", "passed": bool(connectivity.get("reachable"))},
        {"id": "telemetry", "label": "VirtualBox telemetry", "passed": bool(telemetry.get("healthy"))},
        {"id": "readiness", "label": "Lab readiness", "passed": bool(readiness.get("ready"))},
    ]
    return {
        "verified": all(item["passed"] for item in checks),
        "checks": checks,
        "connectivity": connectivity,
        "readiness": readiness,
        "telemetry": {
            "healthy": telemetry.get("healthy"),
            "status": telemetry.get("status"),
            "active_issue": telemetry.get("active_issue"),
        },
    }
