from __future__ import annotations

import json
import subprocess

from app.core.config import ROOT


def run_powershell_script(script: str, *arguments: str) -> str:
    path = ROOT / script
    if not path.exists():
        raise FileNotFoundError(f"PowerShell script not found: {path}")

    command = [
        "powershell.exe",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(path),
        *arguments,
    ]

    completed = subprocess.run(
        command,
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=30,
    )

    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip()
        raise RuntimeError(
            f"PowerShell script failed ({completed.returncode}): {detail}"
        )

    return completed.stdout.strip()


def run_powershell_json(script: str, *arguments: str) -> object:
    output = run_powershell_script(script, *arguments)
    try:
        return json.loads(output)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"Expected JSON from {script}, received: {output[:1000]}"
        ) from exc
