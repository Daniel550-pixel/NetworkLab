from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from typing import Any

from app.services.virtualization_service import get_virtual_network

NETWORK_NAME = "NetworkLab-Lab"
VM_DEFINITIONS = [
    {"name": "NetworkLab-VM01-MGMT", "role": "MGMT", "memory": 2048, "cpus": 2},
    {"name": "NetworkLab-VM02-INFRA", "role": "INFRA", "memory": 2048, "cpus": 2},
    {"name": "NetworkLab-VM03-CLIENT", "role": "CLIENT", "memory": 2048, "cpus": 2},
]


def _vboxmanage() -> str | None:
    candidates = [
        shutil.which("VBoxManage.exe"),
        os.path.join(os.environ.get("VBOX_MSI_INSTALL_PATH", ""), "VBoxManage.exe"),
        os.path.join(os.environ.get("ProgramFiles", ""), "Oracle", "VirtualBox", "VBoxManage.exe"),
        os.path.join(os.environ.get("ProgramFiles", ""), "VirtualBox", "VBoxManage.exe"),
    ]
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return candidate
    return None


def _run(vbox: str, *args: str) -> tuple[bool, str, str]:
    try:
        p = subprocess.run(
            [vbox, *args],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=60,
            check=False,
        )
        return p.returncode == 0, p.stdout.strip(), p.stderr.strip()
    except (OSError, subprocess.SubprocessError) as exc:
        return False, "", str(exc)


def _vms(vbox: str) -> list[dict[str, Any]]:
    ok, out, err = _run(vbox, "list", "vms")
    if not ok:
        raise RuntimeError(err or out or "Unable to query VirtualBox VMs.")

    result = []
    for line in out.splitlines():
        line = line.strip()
        if not line or not line.startswith('"') or '" {' not in line:
            continue
        name, _, rest = line[1:].partition('" {')
        uuid = rest.rstrip("}").strip()
        result.append({"name": name, "uuid": uuid})
    return result


def _find_vm(vbox: str, name: str) -> dict[str, Any] | None:
    return next((vm for vm in _vms(vbox) if vm["name"] == name), None)


def get_vm_topology() -> dict[str, Any]:
    vbox = _vboxmanage()
    if not vbox:
        return {"available": False, "network": NETWORK_NAME, "vms": [], "error": "VBoxManage.exe not found."}

    vms = []
    for definition in VM_DEFINITIONS:
        vm = _find_vm(vbox, definition["name"])
        if not vm:
            vms.append({**definition, "exists": False, "state": "not-created", "network": NETWORK_NAME})
            continue

        ok, show, err = _run(vbox, "showvminfo", definition["name"], "--machinereadable")
        if not ok:
            vms.append({**definition, **vm, "exists": True, "state": "unknown", "network": NETWORK_NAME, "error": err or show})
            continue

        fields = {}
        for line in show.splitlines():
            if "=" in line:
                key, value = line.split("=", 1)
                fields[key] = value.strip('"')

        vms.append({
            **definition,
            **vm,
            "exists": True,
            "state": fields.get("VMState", "unknown"),
            "network": NETWORK_NAME if fields.get("nic1", "").lower() == "hostonly" else "not-attached",
            "nic1": fields.get("nic1", ""),
            "host_only_adapter": fields.get("hostonlyadapter1", ""),
        "firmware": fields.get("firmware", "BIOS"),
        "boot_menu_mode": fields.get("bootmenu", "messageandmenu"),
        "nested_paging": fields.get("nestedpaging", ""),
        })

    return {"available": True, "network": NETWORK_NAME, "vms": vms}


def create_vm_topology() -> dict[str, Any]:
    vbox = _vboxmanage()
    if not vbox:
        raise RuntimeError("VirtualBox VBoxManage.exe was not found.")

    network = get_virtual_network()
    if not network.get("ready"):
        raise RuntimeError("NetworkLab-Lab is not ready. Provision the virtual network first.")
    adapter = (network.get("host_only_adapter") or {}).get("Name")
    if not adapter:
        raise RuntimeError("NetworkLab could not resolve the VirtualBox host-only adapter.")

    for definition in VM_DEFINITIONS:
        name = definition["name"]
        if not _find_vm(vbox, name):
            ok, out, err = _run(vbox, "createvm", "--name", name, "--register")
            if not ok:
                raise RuntimeError(err or out or f"Unable to create {name}.")

        commands = [
            ("modifyvm", name, "--memory", str(definition["memory"]), "--cpus", str(definition["cpus"])),
            ("modifyvm", name, "--nic1", "hostonly", "--hostonlyadapter1", adapter),
        ]
        for args in commands:
            ok, out, err = _run(vbox, *args)
            if not ok:
                raise RuntimeError(err or out or f"Unable to configure {name}.")

    return get_vm_topology()


def get_vm_runtime(name: str) -> dict[str, Any]:
    vbox = _vboxmanage()
    if not vbox:
        raise RuntimeError("VirtualBox VBoxManage.exe was not found.")
    if name not in {item["name"] for item in VM_DEFINITIONS}:
        raise ValueError("Unknown NetworkLab VM.")
    if not _find_vm(vbox, name):
        raise RuntimeError(f"{name} does not exist. Create the VM topology first.")

    ok, show, err = _run(vbox, "showvminfo", name, "--machinereadable")
    if not ok:
        raise RuntimeError(err or show or f"Unable to inspect {name}.")

    fields: dict[str, str] = {}
    for line in show.splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            fields[key.strip('"')] = value.strip('"')

    state = fields.get("VMState", "unknown").lower()
    return {
        "name": name,
        "state": state,
        "running": state == "running",
        "boot_order": [fields.get("boot1", "none"), fields.get("boot2", "none"), fields.get("boot3", "none"), fields.get("boot4", "none")],
        "memory_mb": fields.get("memory", ""),
        "cpus": fields.get("cpus", ""),
        "nic1": fields.get("nic1", ""),
        "host_only_adapter": fields.get("hostonlyadapter1", ""),
    }


def vm_action(name: str, action: str) -> dict[str, Any]:
    vbox = _vboxmanage()
    if not vbox:
        raise RuntimeError("VirtualBox VBoxManage.exe was not found.")
    if name not in {item["name"] for item in VM_DEFINITIONS}:
        raise ValueError("Unknown NetworkLab VM.")

    if not _find_vm(vbox, name):
        raise RuntimeError(f"{name} does not exist. Create the VM topology first.")

    if action == "start":
        args = ("startvm", name, "--type", "headless")
    elif action == "stop":
        args = ("controlvm", name, "acpipowerbutton")
    elif action == "poweroff":
        args = ("controlvm", name, "poweroff")
    else:
        raise ValueError("Unsupported VM action.")

    ok, out, err = _run(vbox, *args)
    if not ok:
        raise RuntimeError(err or out or f"VM action failed: {action}")
    return get_vm_topology()
