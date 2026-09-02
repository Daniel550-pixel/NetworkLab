"""NetworkLab read-only network monitoring baseline."""

from __future__ import annotations

import platform
import socket
from datetime import datetime, timezone


def check_host(host: str) -> dict[str, object]:
    """Resolve a host and return a small, serializable monitoring result."""
    timestamp = datetime.now(timezone.utc).isoformat()
    try:
        address = socket.gethostbyname(host)
        return {
            "timestamp": timestamp,
            "host": host,
            "resolved": True,
            "address": address,
            "platform": platform.system(),
        }
    except socket.gaierror as exc:
        return {
            "timestamp": timestamp,
            "host": host,
            "resolved": False,
            "address": None,
            "platform": platform.system(),
            "error": str(exc),
        }


if __name__ == "__main__":
    print(check_host("localhost"))
