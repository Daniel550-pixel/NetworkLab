"""Read-only system monitoring baseline for NetworkLab."""

from __future__ import annotations

import os
import platform
import shutil
from datetime import datetime, timezone


def collect_system_state() -> dict[str, object]:
    """Collect portable system information without external dependencies."""
    total, used, free = shutil.disk_usage(os.getcwd())
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "platform": platform.platform(),
        "hostname": platform.node(),
        "python_version": platform.python_version(),
        "disk": {
            "total_bytes": total,
            "used_bytes": used,
            "free_bytes": free,
        },
    }


if __name__ == "__main__":
    print(collect_system_state())
