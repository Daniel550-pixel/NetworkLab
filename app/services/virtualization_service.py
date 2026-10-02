from __future__ import annotations

import os
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

NETWORK_NAME = "NetworkLab-Lab"
NETWORK_CIDR = "192.168.77.0/24"
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
        os.path.join(os.environ.get("VBOX_MSI_INSTALL_PATH", ""), "VBoxManage.exe"),
        os.path.join(os.environ.get("ProgramFiles", ""), "Oracle", "VirtualBox", "VBoxManage.exe"),
        os.path.join(os.environ.get("ProgramFiles", ""), "VirtualBox", "VBoxManage.exe"),
    ]
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return candidate
    return None


def _run(vbox: str, *args: str) -> VBoxResult:
    try:
        p = subprocess.run(
            [vbox, *args],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return VBoxResult(False, "", str(exc), 1)
    return VBoxResult(p.returncode == 0, p.stdout.strip(), p.stderr.strip(), p.returncode)


def _records(text: str) -> list[dict[str, str]]:
    """Parse VBoxManage's key/value records without relying on blank lines."""
    records: list[dict[str, str]] = []
    current: dict[str, str] = {}

    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            if current:
                records.append(current)
                current = {}
            continue

        match = re.match(r"^([^:]+):\s*(.*)$", line)
        if not match:
            continue

        key, value = match.group(1).strip(), match.group(2).strip()

        # VBoxManage list output starts each record with Name/NetworkName.
        if key in {"Name", "NetworkName"} and current:
            records.append(current)
            current = {}

        current[key] = value

    if current:
        records.append(current)

    return records


def _find_host_only(vbox: str) -> dict[str, str] | None:
    result = _run(vbox, "list", "hostonlyifs")
    if not result.ok:
        return None

    for item in _records(result.stdout):
        if item.get("IPAddress") == HOST_IP:
            return item
    return None


def _find_dhcp(vbox: str, adapter_name: str | None = None) -> dict[str, str] | None:
    result = _run(vbox, "list", "dhcpservers")
    if not result.ok:
        return None

    expected_network = f"HostInterfaceNetworking-{adapter_name}" if adapter_name else ""
    for item in _records(result.stdout):
        network = item.get("NetworkName", "")
        ip = item.get("IP", "")
        if ip == DHCP_IP or network == expected_network or (
            adapter_name and adapter_name in network
        ):
            return item
    return None


def _base_state() -> dict[str, Any]:
    return {
        "name": NETWORK_NAME,
        "network": NETWORK_CIDR,
        "host_ip": HOST_IP,
        "dhcp": {
            "ip": DHCP_IP,
            "lower": DHCP_LOWER,
            "upper": DHCP_UPPER,
        },
        "internet_access": False,
        "physical_bridge": False,
        "virtualization": "VirtualBox",
    }


def get_virtual_network() -> dict[str, Any]:
    vbox = _vboxmanage()
    base = _base_state()

    if not vbox:
        return {
            **base,
            "available": False,
            "exists": False,
            "ready": False,
            "error": "VBoxManage.exe not found. Install VirtualBox or expose VBoxManage.exe on PATH.",
        }

    host = _find_host_only(vbox)
    dhcp = _find_dhcp(vbox, host.get("Name") if host else None)
    ready = host is not None and dhcp is not None

    return {
        **base,
        "available": True,
        "exists": host is not None,
        "ready": ready,
        "host_only_adapter": host,
        "dhcp_server": dhcp,
    }


def create_virtual_network() -> dict[str, Any]:
    vbox = _vboxmanage()
    if not vbox:
        raise RuntimeError(
            "VirtualBox VBoxManage.exe was not found. Install VirtualBox or add its installation directory to PATH."
        )

    host = _find_host_only(vbox)

    if not host:
        created = _run(vbox, "hostonlyif", "create")
        if not created.ok:
            raise RuntimeError(
                created.stderr or created.stdout or "Unable to create the VirtualBox host-only adapter."
            )

        # The create command normally reports the adapter name in stdout.
        match = re.search(r"Name:\s*([^\r\n]+)", created.stdout, re.IGNORECASE)
        adapter_name = match.group(1).strip() if match else None

        host = _find_host_only(vbox)

        # If the adapter still has VirtualBox's default address, resolve it
        # by the reported name and configure it below.
        if not host and adapter_name:
            result = _run(vbox, "list", "hostonlyifs")
            for item in _records(result.stdout):
                if item.get("Name") == adapter_name:
                    host = item
                    break

    if not host or not host.get("Name"):
        raise RuntimeError(
            "VirtualBox created a host-only adapter, but NetworkLab could not resolve its adapter name."
        )

    adapter_name = host["Name"]

    configured = _run(
        vbox,
        "hostonlyif",
        "ipconfig",
        adapter_name,
        "--ip",
        HOST_IP,
        "--netmask",
        NETMASK,
    )
    if not configured.ok:
        raise RuntimeError(
            configured.stderr or configured.stdout or "Unable to configure the NetworkLab host-only adapter."
        )

    dhcp = _find_dhcp(vbox, adapter_name)
    if not dhcp:
        dhcp_result = _run(
            vbox,
            "dhcpserver",
            "add",
            "--ifname",
            adapter_name,
            "--ip",
            DHCP_IP,
            "--netmask",
            NETMASK,
            "--lowerip",
            DHCP_LOWER,
            "--upperip",
            DHCP_UPPER,
            "--enable",
        )
        if not dhcp_result.ok:
            raise RuntimeError(
                dhcp_result.stderr
                or dhcp_result.stdout
                or "Unable to create the NetworkLab DHCP server."
            )

    final = get_virtual_network()
    if not final.get("ready"):
        raise RuntimeError(
            "Virtual network provisioning completed without producing the expected host-only adapter and DHCP state."
        )

    return final
