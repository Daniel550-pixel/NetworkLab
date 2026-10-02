from __future__ import annotations

import os
import shutil
import subprocess
import threading
import time
from datetime import datetime, timezone
from typing import Any

MONITOR_INTERVAL_SECONDS = int(os.environ.get("NETWORKLAB_VBOX_MONITOR_INTERVAL", "60"))
REPAIR_THRESHOLD = int(os.environ.get("NETWORKLAB_VBOX_REPAIR_THRESHOLD", "3"))
REPAIR_COOLDOWN_SECONDS = int(os.environ.get("NETWORKLAB_VBOX_REPAIR_COOLDOWN", "600"))

_lock = threading.Lock()
_state: dict[str, Any] = {
    "status": "unknown",
    "healthy": False,
    "consecutive_failures": 0,
    "last_check": None,
    "last_repair": None,
    "last_repair_result": None,
    "last_error": None,
    "monitor_running": False,
}


def _find_vboxmanage() -> str | None:
    candidates = [
        shutil.which("VBoxManage.exe"),
        os.path.join(os.environ.get("VBOX_MSI_INSTALL_PATH", ""), "VBoxManage.exe"),
        os.path.join(os.environ.get("ProgramFiles", ""), "Oracle", "VirtualBox", "VBoxManage.exe"),
        os.path.join(os.environ.get("ProgramFiles", ""), "VirtualBox", "VBoxManage.exe"),
    ]
    for candidate in candidates:
        if candidate and os.path.isfile(candidate):
            return candidate
    return None


def _run(vbox: str, *args: str, timeout: int = 15) -> tuple[bool, str, str]:
    try:
        result = subprocess.run(
            [vbox, *args],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return False, "", str(exc)

    return result.returncode == 0, result.stdout.strip(), result.stderr.strip()


def _combined_error(stdout: str, stderr: str) -> str:
    return "\n".join(part for part in (stderr, stdout) if part).strip()


def _is_com_lock_error(detail: str) -> bool:
    lowered = detail.lower()
    markers = (
        "e_accessdenied",
        "e_unexpected",
        "the object is not ready",
        "the session is not locked",
        "session state: unlocked",
        "bandwidthcontrolwrap",
        "sessionmachine",
        "unlockmachine",
    )
    return any(marker in lowered for marker in markers)


def _running_vms(vbox: str) -> tuple[bool, list[str], str]:
    ok, stdout, stderr = _run(vbox, "list", "runningvms")
    if not ok:
        return False, [], _combined_error(stdout, stderr)

    names: list[str] = []
    for line in stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        if '"' in line:
            names.append(line.split('"')[1])
        else:
            names.append(line)
    return True, names, ""


def _probe(vbox: str) -> dict[str, Any]:
    probes = (
        ("hostonlyifs", ("list", "hostonlyifs")),
        ("dhcpservers", ("list", "dhcpservers")),
        ("vms", ("list", "vms")),
    )

    failures: list[dict[str, str]] = []
    for name, args in probes:
        ok, stdout, stderr = _run(vbox, *args)
        if not ok:
            detail = _combined_error(stdout, stderr)
            failures.append(
                {
                    "probe": name,
                    "error": detail or f"VBoxManage {' '.join(args)} failed.",
                }
            )

    return {
        "ok": not failures,
        "failures": failures,
    }


def _restart_vboxsvc_if_safe(vbox: str) -> dict[str, Any]:
    running_ok, running_vms, running_error = _running_vms(vbox)
    if not running_ok:
        return {
            "attempted": False,
            "success": False,
            "reason": f"Could not verify running VMs; repair aborted: {running_error}",
        }

    if running_vms:
        return {
            "attempted": False,
            "success": False,
            "reason": "Repair skipped because VirtualBox VMs are currently running.",
            "running_vms": running_vms,
        }

    taskkill = subprocess.run(
        ["taskkill.exe", "/F", "/IM", "VBoxSVC.exe"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=15,
        check=False,
    )

    time.sleep(2)

    ok, stdout, stderr = _run(vbox, "list", "vms")
    detail = _combined_error(stdout, stderr)

    return {
        "attempted": True,
        "success": ok,
        "action": "restart_vboxsvc",
        "taskkill_returncode": taskkill.returncode,
        "verification_error": detail if not ok else None,
        "message": "VBoxSVC was restarted and VBoxManage recovered."
        if ok
        else "VBoxSVC restart was attempted, but VBoxManage is still unhealthy.",
    }


def check_and_recover(force_repair: bool = False) -> dict[str, Any]:
    now = datetime.now(timezone.utc).isoformat()
    with _lock:
        vbox = _find_vboxmanage()

        if not vbox:
            _state.update(
                {
                    "status": "failed",
                    "healthy": False,
                    "last_check": now,
                    "last_error": "VBoxManage.exe not found.",
                }
            )
            return dict(_state)

        probe = _probe(vbox)
        if probe["ok"]:
            _state.update(
                {
                    "status": "healthy",
                    "healthy": True,
                    "consecutive_failures": 0,
                    "last_check": now,
                    "last_error": None,
                }
            )
            return {
                **_state,
                "vboxmanage": vbox,
                "probe": probe,
            }

        _state["consecutive_failures"] = int(_state["consecutive_failures"]) + 1
        _state["last_check"] = now
        _state["healthy"] = False
        _state["status"] = "degraded"
        _state["last_error"] = probe["failures"]

        should_repair = force_repair or (
            int(_state["consecutive_failures"]) >= REPAIR_THRESHOLD
        )

        if _state["last_repair"]:
            try:
                last_repair = datetime.fromisoformat(
                    str(_state["last_repair"]).replace("Z", "+00:00")
                )
                elapsed = (datetime.now(timezone.utc) - last_repair).total_seconds()
                if elapsed < REPAIR_COOLDOWN_SECONDS and not force_repair:
                    should_repair = False
            except ValueError:
                pass

        if not should_repair:
            return {
                **_state,
                "vboxmanage": vbox,
                "probe": probe,
                "repair_pending": _is_com_lock_error(
                    "\n".join(item["error"] for item in probe["failures"])
                ),
            }

        repair = _restart_vboxsvc_if_safe(vbox)
        _state["last_repair"] = now
        _state["last_repair_result"] = repair

        verification = _probe(vbox)
        if verification["ok"]:
            _state.update(
                {
                    "status": "repaired",
                    "healthy": True,
                    "consecutive_failures": 0,
                    "last_error": None,
                }
            )
        else:
            _state.update(
                {
                    "status": "failed",
                    "healthy": False,
                    "last_error": verification["failures"],
                }
            )

        return {
            **_state,
            "vboxmanage": vbox,
            "probe": verification,
            "repair": repair,
        }


def get_telemetry() -> dict[str, Any]:
    return check_and_recover(force_repair=False)


def start_monitor() -> None:
    with _lock:
        if _state["monitor_running"]:
            return
        _state["monitor_running"] = True

    def _loop() -> None:
        while True:
            try:
                check_and_recover()
            except Exception as exc:
                with _lock:
                    _state["status"] = "failed"
                    _state["healthy"] = False
                    _state["last_error"] = str(exc)
            time.sleep(max(10, MONITOR_INTERVAL_SECONDS))

    thread = threading.Thread(
        target=_loop,
        name="NetworkLab-VBoxTelemetry",
        daemon=True,
    )
    thread.start()
