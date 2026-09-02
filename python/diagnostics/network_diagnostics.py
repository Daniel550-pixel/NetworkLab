"""Read-only network diagnostics for NetworkLab."""

from __future__ import annotations

import socket
from datetime import datetime, timezone


def tcp_check(host: str, port: int, timeout: float = 2.0) -> dict[str, object]:
    """Check whether a TCP endpoint accepts a connection."""
    started = datetime.now(timezone.utc)
    try:
        with socket.create_connection((host, port), timeout=timeout):
            reachable = True
            error = None
    except OSError as exc:
        reachable = False
        error = str(exc)

    return {
        "timestamp": started.isoformat(),
        "host": host,
        "port": port,
        "reachable": reachable,
        "error": error,
    }


if __name__ == "__main__":
    print(tcp_check("127.0.0.1", 80))
