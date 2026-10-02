from __future__ import annotations

LAB_ID = "NetworkLab-Lab"

VM_ROLES = [
    {
        "name": "NetworkLab-VM01-MGMT",
        "hostname": "nl-mgmt",
        "role": "MGMT",
        "purpose": "Management workstation and administration entry point.",
        "address_mode": "dhcp-reservation",
        "recommended_ip": "192.168.77.10",
    },
    {
        "name": "NetworkLab-VM02-INFRA",
        "hostname": "nl-infra",
        "role": "INFRA",
        "purpose": "Infrastructure services host for lab services.",
        "address_mode": "dhcp-reservation",
        "recommended_ip": "192.168.77.20",
    },
    {
        "name": "NetworkLab-VM03-CLIENT",
        "hostname": "nl-client",
        "role": "CLIENT",
        "purpose": "Client endpoint used for connectivity and service validation.",
        "address_mode": "dhcp-reservation",
        "recommended_ip": "192.168.77.30",
    },
]

LAB_PHASES = [
    {"id": "network", "name": "Virtual network", "action": "create_virtual_network"},
    {"id": "topology", "name": "VM topology", "action": "create_vm_topology"},
    {"id": "storage", "name": "VM storage", "action": "create_vm_storage"},
    {"id": "media", "name": "OS media", "action": "manual_iso"},
    {"id": "guest", "name": "Guest configuration", "action": "manual_guest_install"},
    {"id": "verification", "name": "Verification", "action": "run_verification"},
]
