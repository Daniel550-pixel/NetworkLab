from __future__ import annotations

import os
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

NETWORK_NAME = "NetworkLab-Lab"
HOST_IP = "192.168.77.1"
NETMASK = "255.255.255.0"
DHCP_IP = "192.168.77.2"
DHCP_LOWER = "192.168.77.100"
DHCP_UPPER = "192.168.77.200"


@dataclass
class VBoxResult:
    ok: bool
    stdout: str
    stderr: str
    returncode: int


def _vboxmanage() -> str | None:
    candidates = [
        shutil.which("VBoxManage.exe"),
        os.path.join(os.environ.get("ProgramFiles", ""), "Oracle", "VirtualBox", "VBoxManage.exe"),
        os.path.join(os.environ.get("ProgramFiles", ""), "VirtualBox", "VBoxManage.exe"),
    ]
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return candidate
    return None


def _run(vbox: str, *args: str) -> VBoxResult:
    p = subprocess.run(
        [vbox, *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=30,
    )
    return VBoxResult(p.returncode == 0, p.stdout.strip(), p.stderr.strip(), p.returncode)


def _blocks(text: str) -> list[dict[str, str]]:
    blocks: list[dict[str, str]] = []
    current: dict[str, str] = {}
    for line in text.splitlines():
        if not line.strip():
            if current:
                blocks.append(current)
                current = {}
            continue
        if ":" in line:
            key, value = line.split(":", 1)
            current[key.strip()] = value.strip()
    if current:
        blocks.append(current)
    return blocks


def _find_host_only(vbox: str) -> dict[str, str] | None:
    result = _run(vbox, "list", "hostonlyifs")
    if not result.ok:
        return None
    for item in _blocks(result.stdout):
        if item.get("IPAddress") == HOST_IP:
            return item
    return None


def _find_dhcp(vbox: str, adapter_name: str | None = None) -> dict[str, str] | None:
    result = _run(vbox, "list", "dhcpservers")
    if not result.ok:
        return None
    for item in _blocks(result.stdout):
        network = item.get("NetworkName", "")
        ip = item.get("IP", "")
        if (adapter_name and adapter_name in network) or ip == DHCP_IP:
            return item
    return None


def get_virtual_network() -> dict[str, Any]:
    vbox = _vboxmanage()
    base = {
        "name": NETWORK_NAME,
        "network": "192.168.77.0/24",
        "host_ip": HOST_IP,
        "dhcp": {"ip": DHCP_IP, "lower": DHCP_LOWER, "upper": DHCP_UPPER},
        "internet_access": False,
        "physical_bridge": False,
        "virtualization": "VirtualBox",
    }
    if not vbox:
        return {**base, "available": False, "exists": False, "error": "VBoxManage.exe not found"}

    host = _find_host_only(vbox)
    dhcp = _find_dhcp(vbox, host.get("Name") if host else None)
    return {
        **base,
        "available": True,
        "exists": host is not None,
        "host_only_adapter": host,
        "dhcp_server": dhcp,
    }


def create_virtual_network() -> dict[str, Any]:
    vbox = _vboxmanage()
    if not vbox:
        raise RuntimeError("VirtualBox VBoxManage.exe was not found.")

    host = _find_host_only(vbox)
    if not host:
        created = _run(vbox, "hostonlyif", "create")
        if not created.ok:
            raise RuntimeError(created.stderr or created.stdout or "Unable to create host-only adapter.")
        match = re.search(r"Name:\s*([^\r\n]+)", created.stdout)
        adapter_name = match.group(1).strip() if match else None
        host = _find_host_only(vbox)
        if not host and adapter_name:
            result = _run(vbox, "list", "hostonlyifs")
            for item in _blocks(result.stdout):
                if item.get("Name") == adapter_name:
                    host = item
                    break

    if not host:
        raise RuntimeError("VirtualBox created an adapter, but its identity could not be resolved.")

    adapter_name = host["Name"]
    configured = _run(vbox, "hostonlyif", "ipconfig", adapter_name, "--ip", HOST_IP, "--netmask", NETMASK)
    if not configured.ok:
        raise RuntimeError(configured.stderr or configured.stdout or "Unable to configure host-only adapter.")

    dhcp = _find_dhcp(vbox, adapter_name)
    if not dhcp:
        dhcp_result = _run(
            vbox,
            "dhcpserver", "add",
            "--ifname", adapter_name,
            "--ip", DHCP_IP,
            "--netmask", NETMASK,
            "--lowerip", DHCP_LOWER,
            "--upperip", DHCP_UPPER,
            "--enable",
        )
        if not dhcp_result.ok:
            raise RuntimeError(dhcp_result.stderr or dhcp_result.stdout or "Unable to create DHCP server.")

    return get_virtual_network()
