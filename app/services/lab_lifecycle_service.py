from __future__ import annotations

from typing import Any

from app.services.lab_definition import LAB_ID, LAB_PHASES, VM_ROLES
from app.services.virtualization_service import create_virtual_network, get_virtual_network
from app.services.vm_service import create_vm_topology, get_vm_topology
from app.services.storage_service import create_vm_storage, get_vm_storage
from app.services.readiness_service import get_lab_readiness

def get_lab_definition() -> dict[str, Any]:
    return {
        "lab_id": LAB_ID,
        "network": {
            "name": LAB_ID,
            "cidr": "192.168.77.0/24",
            "host_ip": "192.168.77.1",
            "dhcp": {"ip": "192.168.77.2", "range": ["192.168.77.100", "192.168.77.200"]},
            "internet_access": False,
        },
        "roles": VM_ROLES,
        "phases": LAB_PHASES,
    }

def prepare_lab() -> dict[str, Any]:
    phases: list[dict[str, Any]] = []
    try:
        network = create_virtual_network()
        phases.append({"id": "network", "status": "completed", "result": network})
        topology = create_vm_topology()
        phases.append({"id": "topology", "status": "completed", "result": topology})
        storage = create_vm_storage()
        phases.append({"id": "storage", "status": "completed", "result": storage})
    except Exception as exc:
        phases.append({"id": "current", "status": "failed", "error": str(exc)})
        return {"success": False, "lab": get_lab_definition(), "phases": phases, "readiness": get_lab_readiness()}

    return {"success": True, "lab": get_lab_definition(), "phases": phases, "readiness": get_lab_readiness()}

def get_lab_state() -> dict[str, Any]:
    return {
        "definition": get_lab_definition(),
        "network": get_virtual_network(),
        "topology": get_vm_topology(),
        "storage": get_vm_storage(),
        "readiness": get_lab_readiness(),
    }
