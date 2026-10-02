from app.services.storage_service import get_vm_storage
from app.services.virtualization_service import get_virtual_network
from app.services.vm_service import get_vm_topology

EXPECTED_VMS = {
    "NetworkLab-VM01-MGMT",
    "NetworkLab-VM02-INFRA",
    "NetworkLab-VM03-CLIENT",
}


def get_lab_readiness():
    network = get_virtual_network()
    topology = get_vm_topology()
    storage = get_vm_storage()

    topology_vms = topology.get("vms", []) if isinstance(topology, dict) else []
    storage_vms = storage.get("vms", []) if isinstance(storage, dict) else []

    vm_names = {
        vm.get("name")
        for vm in topology_vms
        if isinstance(vm, dict) and vm.get("name")
    }
    storage_by_name = {
        item.get("name"): item
        for item in storage_vms
        if isinstance(item, dict) and item.get("name")
    }

    network_ready = bool(network.get("ready"))
    vm_ready = (
        vm_names == EXPECTED_VMS
        and all(
            vm.get("network") == "NetworkLab-Lab"
            for vm in topology_vms
            if isinstance(vm, dict) and vm.get("name") in EXPECTED_VMS
        )
    )
    storage_ready = all(
        name in storage_by_name and bool(storage_by_name[name].get("disk"))
        for name in EXPECTED_VMS
    )
    media_ready = all(
        name in storage_by_name and bool(storage_by_name[name].get("iso"))
        for name in EXPECTED_VMS
    )
    boot_ready = media_ready
    runtime_ready = vm_ready and storage_ready

    steps = [
        {"id": "network", "label": "Network", "ready": network_ready},
        {"id": "vms", "label": "VM topology", "ready": vm_ready},
        {"id": "storage", "label": "Storage", "ready": storage_ready},
        {"id": "media", "label": "OS media", "ready": media_ready},
        {"id": "boot", "label": "Boot readiness", "ready": boot_ready},
        {"id": "runtime", "label": "Runtime", "ready": runtime_ready},
    ]

    completed = sum(step["ready"] for step in steps)
    next_step = next((step["id"] for step in steps if not step["ready"]), None)

    return {
        "ready": completed == len(steps),
        "completed": completed,
        "total": len(steps),
        "next_step": next_step,
        "steps": steps,
    }
