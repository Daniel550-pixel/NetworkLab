from __future__ import annotations

import socket
import subprocess
from typing import Any

from app.services.lab_definition import VM_ROLES

DEFAULT_TIMEOUT = 2.0

def _ping(ip: str) -> dict[str, Any]:
    try:
        result = subprocess.run(
            ["ping", "-n", "1", "-w", "1200", ip],
            capture_output=True,
            text=True,
            timeout=3,
        )
        return {"reachable": result.returncode == 0, "method": "icmp", "detail": result.stdout[-300:]}
    except Exception as exc:
        return {"reachable": False, "method": "icmp", "detail": str(exc)}

def _tcp(ip: str, port: int) -> dict[str, Any]:
    try:
        with socket.create_connection((ip, port), timeout=DEFAULT_TIMEOUT):
            return {"reachable": True, "port": port, "method": "tcp"}
    except Exception as exc:
        return {"reachable": False, "port": port, "method": "tcp", "detail": str(exc)}

def validate_lab_connectivity() -> dict[str, Any]:
    endpoints = []
    for role in VM_ROLES:
        ip = role["recommended_ip"]
        endpoints.append({
            "vm": role["name"],
            "role": role["role"],
            "ip": ip,
            "icmp": _ping(ip),
            "expected_services": {
                "dns": _tcp(ip, 53) if role["role"] == "INFRA" else {"skipped": True},
                "dhcp": {"protocol": "udp", "port": 67, "status": "not-probed"},
                "management": _tcp(ip, 3389) if role["role"] == "MGMT" else {"skipped": True},
            },
        })

    pairs = []
    for source in VM_ROLES:
        for target in VM_ROLES:
            if source["name"] == target["name"]:
                continue
            pairs.append({
                "source": source["name"],
                "target": target["name"],
                "target_ip": target["recommended_ip"],
                "status": "host-probe-only",
                "note": "Guest-to-guest validation requires installed and configured guests.",
            })

    return {
        "network": "NetworkLab-Lab",
        "mode": "host-assisted",
        "endpoints": endpoints,
        "pairs": pairs,
    }
