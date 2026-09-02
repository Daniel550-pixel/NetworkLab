"""Run a read-only monitoring cycle using only the Python standard library."""

from __future__ import annotations

import json
import socket
from datetime import datetime, timezone
from pathlib import Path

CONFIG = Path(__file__).resolve().parents[2] / 'config' / 'lab-config.json'


def load_config() -> dict:
    return json.loads(CONFIG.read_text(encoding='utf-8'))


def check_host(host: str) -> dict[str, object]:
    timestamp = datetime.now(timezone.utc).isoformat()
    try:
        address = socket.gethostbyname(host)
        return {'timestamp': timestamp, 'host': host, 'resolved': True, 'address': address}
    except socket.gaierror as exc:
        return {'timestamp': timestamp, 'host': host, 'resolved': False, 'address': None, 'error': str(exc)}


def run() -> dict[str, object]:
    config = load_config()
    targets = config.get('monitoring', {}).get('connectivity_targets', [])
    return {
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'environment': config.get('environment'),
        'checks': [check_host(host) for host in targets],
    }


if __name__ == '__main__':
    print(json.dumps(run(), indent=2))
