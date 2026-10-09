from __future__ import annotations

from app.services.lab_definition import VM_ROLES

ROLE_CONTRACTS = {
    "MGMT": {
        "required": ["hostname", "network", "ip", "dns", "administrator_access"],
        "services": ["remote-management", "diagnostics"],
        "validation": ["host-reachable", "dns-resolution", "admin-access"],
    },
    "INFRA": {
        "required": ["hostname", "network", "ip", "dns", "service_stack"],
        "services": ["dns", "dhcp", "lab-services"],
        "validation": ["host-reachable", "dns-listening", "dhcp-configured"],
    },
    "CLIENT": {
        "required": ["hostname", "network", "ip", "dns"],
        "services": ["client-networking"],
        "validation": ["host-reachable", "dns-resolution", "dhcp-lease"],
    },
}

def get_guest_contracts() -> dict:
    contracts = []
    for role in VM_ROLES:
        contract = ROLE_CONTRACTS[role["role"]]
        contracts.append({
            "vm": role["name"],
            "hostname": role["hostname"],
            "role": role["role"],
            "recommended_ip": role["recommended_ip"],
            "purpose": role["purpose"],
            "required": list(contract["required"]),
            "services": list(contract["services"]),
            "validation": list(contract["validation"]),
            "status": "guest-install-required",
            "os_agnostic": True,
        })
    return {"contracts": contracts, "os_selection": "manual", "automation_boundary": "guest-agent-or-manual-bootstrap"}

def get_guest_contract(vm_name: str) -> dict | None:
    return next((item for item in get_guest_contracts()["contracts"] if item["vm"] == vm_name), None)
