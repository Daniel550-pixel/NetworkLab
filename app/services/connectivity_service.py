from __future__ import annotations

import ipaddress
import platform
import subprocess
from typing import Any

from app.services.virtualization_service import get_virtual_network

DEFAULT_TARGETS = ("127.0.0.1",)

def _ping(target: str, timeout_ms: int = 1000) -> dict[str, Any]:
    command = ["ping.exe", "-n", "1", "-w", str(timeout_ms), target]
    try:
        result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8",
                                errors="replace", timeout=max(3, timeout_ms / 1000 + 2), check=False)
    except (OSError, subprocess.SubprocessError) as exc:
        return {"target": target, "reachable": False, "error": str(exc)}
    return {
        "target": target,
        "reachable": result.returncode == 0,
        "output": (result.stdout or result.stderr).strip()[-1000:],
    }

def get_connectivity_state() -> dict[str, Any]:
    network = get_virtual_network()
    targets = list(DEFAULT_TARGETS)
    if isinstance(network, dict) and network.get("host_ip"):
        host_ip = str(network["host_ip"])
        try:
            ipaddress.ip_address(host_ip)
            targets.append(host_ip)
        except ValueError:
            pass
    results = [_ping(target) for target in dict.fromkeys(targets)]
    return {
        "platform": platform.system(),
        "read_only": True,
        "network": network,
        "targets": results,
        "reachable": all(item["reachable"] for item in results),
    }
