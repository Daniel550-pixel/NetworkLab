from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from app.services.vm_service import VM_DEFINITIONS, _find_vm, _vboxmanage, _run

DISK_SIZE_MB = 20 * 1024
STORAGE_CONTROLLER = "NetworkLab-SATA"
DISK_FORMAT = "VDI"


def _machine_fields(vbox: str, name: str) -> dict[str, str]:
    ok, out, err = _run(vbox, "showvminfo", name, "--machinereadable")
    if not ok:
        raise RuntimeError(err or out or f"Unable to inspect {name}.")
    fields: dict[str, str] = {}
    for line in out.splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            fields[key.strip('"')] = value.strip('"')
    return fields


def _disk_path(vbox: str, name: str) -> Path:
    fields = _machine_fields(vbox, name)
    cfg = fields.get("CfgFile")
    if cfg:
        return Path(cfg).parent / f"{name}.vdi"
    base = Path(os.environ.get("USERPROFILE", str(Path.home()))) / "VirtualBox VMs" / name
    return base / f"{name}.vdi"


def _storage_for_vm(vbox: str, definition: dict[str, Any]) -> dict[str, Any]:
    name = definition["name"]
    vm = _find_vm(vbox, name)
    if not vm:
        return {**definition, "exists": False, "disk": None, "iso": None}

    fields = _machine_fields(vbox, name)
    disk = (
        fields.get("SATA-0-0")
        or fields.get("NetworkLab-SATA-0-0")
        or fields.get("SATA-0-1")
        or fields.get("NetworkLab-SATA-0-1")
    )
    iso = (
        fields.get("SATA-1-0")
        or fields.get("NetworkLab-SATA-1-0")
        or fields.get("IDE-1-0")
    )
    return {
        **definition,
        "exists": True,
        "disk": disk or None,
        "disk_path": str(_disk_path(vbox, name)) if disk else None,
        "iso": iso if iso and iso.lower() != "none" else None,
        "storage_controller": STORAGE_CONTROLLER if fields.get("storagecontrollername0") else None,
    }


def attach_vm_iso(name: str, iso_path: str) -> dict[str, Any]:
    vbox = _vboxmanage()
    if not vbox:
        raise RuntimeError("VirtualBox VBoxManage.exe was not found.")
    if name not in {item["name"] for item in VM_DEFINITIONS}:
        raise ValueError("Unknown NetworkLab VM.")
    if not _find_vm(vbox, name):
        raise RuntimeError(f"{name} does not exist. Create the VM topology first.")

    path = Path(iso_path).expanduser().resolve()
    if not path.is_file():
        raise RuntimeError(f"ISO file does not exist: {path}")
    if path.suffix.lower() != ".iso":
        raise RuntimeError("OS media must be an .iso file.")

    fields = _machine_fields(vbox, name)
    if not fields.get("storagecontrollername0"):
        raise RuntimeError(f"{name} has no {STORAGE_CONTROLLER} controller. Create VM storage first.")

    ok, out, err = _run(
        vbox, "storageattach", name, "--storagectl", STORAGE_CONTROLLER,
        "--port", "1", "--device", "0", "--type", "dvddrive",
        "--medium", str(path),
    )
    if not ok:
        raise RuntimeError(err or out or f"Unable to attach ISO to {name}.")

    ok, out, err = _run(
        vbox, "modifyvm", name, "--boot1", "dvd", "--boot2", "disk",
        "--boot3", "none", "--boot4", "none",
    )
    if not ok:
        raise RuntimeError(err or out or f"Unable to configure boot order for {name}.")
    return get_vm_storage()


def eject_vm_iso(name: str) -> dict[str, Any]:
    vbox = _vboxmanage()
    if not vbox:
        raise RuntimeError("VirtualBox VBoxManage.exe was not found.")
    if name not in {item["name"] for item in VM_DEFINITIONS}:
        raise ValueError("Unknown NetworkLab VM.")
    if not _find_vm(vbox, name):
        raise RuntimeError(f"{name} does not exist. Create the VM topology first.")

    ok, out, err = _run(
        vbox, "storageattach", name, "--storagectl", STORAGE_CONTROLLER,
        "--port", "1", "--device", "0", "--type", "dvddrive", "--medium", "none",
    )
    if not ok:
        raise RuntimeError(err or out or f"Unable to eject ISO from {name}.")

    ok, out, err = _run(
        vbox, "modifyvm", name, "--boot1", "disk", "--boot2", "none",
        "--boot3", "none", "--boot4", "none",
    )
    if not ok:
        raise RuntimeError(err or out or f"Unable to restore disk boot order for {name}.")
    return get_vm_storage()


def get_vm_storage() -> dict[str, Any]:
    vbox = _vboxmanage()
    if not vbox:
        return {"available": False, "vms": [], "error": "VBoxManage.exe not found."}
    return {
        "available": True,
        "disk_size_gb": DISK_SIZE_MB // 1024,
        "disk_format": DISK_FORMAT,
        "vms": [_storage_for_vm(vbox, definition) for definition in VM_DEFINITIONS],
    }


def create_vm_storage() -> dict[str, Any]:
    vbox = _vboxmanage()
    if not vbox:
        raise RuntimeError("VirtualBox VBoxManage.exe was not found.")

    for definition in VM_DEFINITIONS:
        name = definition["name"]
        if not _find_vm(vbox, name):
            raise RuntimeError(f"{name} does not exist. Create the VM topology first.")

        fields = _machine_fields(vbox, name)
        controller = fields.get("storagecontrollername0")
        if not controller:
            ok, out, err = _run(
                vbox, "storagectl", name, "--name", STORAGE_CONTROLLER,
                "--add", "sata", "--controller", "IntelAhci", "--portcount", "4",
            )
            if not ok:
                raise RuntimeError(err or out or f"Unable to create storage controller for {name}.")

        fields = _machine_fields(vbox, name)
        disk_attached = bool(fields.get("SATA-0-0") or fields.get(f"{STORAGE_CONTROLLER}-0-0"))
        disk_path = _disk_path(vbox, name)

        if not disk_attached:
            if not disk_path.is_file():
                disk_path.parent.mkdir(parents=True, exist_ok=True)
                ok, out, err = _run(
                    vbox, "createhd", "--filename", str(disk_path),
                    "--size", str(DISK_SIZE_MB), "--format", DISK_FORMAT,
                )
                if not ok:
                    raise RuntimeError(err or out or f"Unable to create disk for {name}.")

            ok, out, err = _run(
                vbox, "storageattach", name, "--storagectl", STORAGE_CONTROLLER,
                "--port", "0", "--device", "0", "--type", "hdd",
                "--medium", str(disk_path),
            )
            if not ok:
                raise RuntimeError(err or out or f"Unable to attach disk to {name}.")

    return get_vm_storage()
