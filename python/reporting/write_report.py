"""Persist a monitoring result as a timestamped JSON evidence file."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


def write_report(report: dict[str, object], output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    path = output_dir / f'monitoring-{stamp}.json'
    path.write_text(json.dumps(report, indent=2), encoding='utf-8')
    return path


if __name__ == '__main__':
    from runpy import run_path

    monitor_path = Path(__file__).resolve().parents[1] / 'monitoring' / 'run_monitor.py'
    result = run_path(str(monitor_path))
    report = result['run']()
    output = write_report(report, Path(__file__).resolve().parents[2] / 'logs')
    print(output)
