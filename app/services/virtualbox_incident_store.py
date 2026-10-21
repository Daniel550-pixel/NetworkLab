from __future__ import annotations

import json
import os
import threading
from collections import deque
from pathlib import Path
from typing import Any

DEFAULT_PATH = Path(
    os.environ.get(
        "NETWORKLAB_VBOX_INCIDENT_LOG",
        Path(__file__).resolve().parents[2] / "data" / "virtualbox_incidents.json",
    )
)
MAX_EVENTS = int(os.environ.get("NETWORKLAB_VBOX_INCIDENT_HISTORY", "500"))
_lock = threading.RLock()


def _load() -> deque[dict[str, Any]]:
    try:
        if not DEFAULT_PATH.exists():
            return deque(maxlen=MAX_EVENTS)
        payload = json.loads(DEFAULT_PATH.read_text(encoding="utf-8"))
        if not isinstance(payload, list):
            return deque(maxlen=MAX_EVENTS)
        return deque(
            [item for item in payload if isinstance(item, dict)],
            maxlen=MAX_EVENTS,
        )
    except (OSError, json.JSONDecodeError):
        return deque(maxlen=MAX_EVENTS)


_events = _load()


def record(event: dict[str, Any]) -> None:
    with _lock:
        _events.appendleft(event)
        DEFAULT_PATH.parent.mkdir(parents=True, exist_ok=True)
        temporary = DEFAULT_PATH.with_suffix(".tmp")
        temporary.write_text(
            json.dumps(list(_events), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        temporary.replace(DEFAULT_PATH)


def history() -> list[dict[str, Any]]:
    with _lock:
        return list(_events)


def path() -> str:
    return str(DEFAULT_PATH)
