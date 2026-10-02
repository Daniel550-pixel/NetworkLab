from __future__ import annotations

import json
import os
import shutil
import subprocess
import threading
import time
from collections import deque
from datetime import datetime, timezone
from typing import Any

from app.services.virtualbox_incident_store import history as persistent_history
from app.services.virtualbox_incident_store import path as incident_log_path
from app.services.virtualbox_incident_store import record as persist_event

MONITOR_INTERVAL_SECONDS = int(os.environ.get("NETWORKLAB_VBOX_MONITOR_INTERVAL", "60"))
REPAIR_THRESHOLD = int(os.environ.get("NETWORKLAB_VBOX_REPAIR_THRESHOLD", "3"))
REPAIR_COOLDOWN_SECONDS = int(os.environ.get("NETWORKLAB_VBOX_REPAIR_COOLDOWN", "600"))
PROBE_TIMEOUT_SECONDS = int(os.environ.get("NETWORKLAB_VBOX_PROBE_TIMEOUT", "15"))
MAX_HISTORY = int(os.environ.get("NETWORKLAB_VBOX_HISTORY", "100"))

_lock = threading.RLock()
_history: deque[dict[str, Any]] = deque(maxlen=MAX_HISTORY)
_state: dict[str, Any] = {
    "status": "unknown",
    "healthy": False,
    "consecutive_failures": 0,
    "last_check": None,
    "last_repair": None,
    "last_repair_result": None,
    "last_error": None,
    "monitor_running": False,
    "repair_count": 0,
    "active_incident": False,
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _record(event: str, **data: Any) -> None:
    item = {"timestamp": _now(), "event": event, **data}
    _history.appendleft(item)
    try:
        persist_event(item)
    except (OSError, TypeError, ValueError):
        pass


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


def _run(vbox: str, *args: str, timeout: int = PROBE_TIMEOUT_SECONDS) -> tuple[bool, str, str]:
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
        "comget_",
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
    passed: list[str] = []

    for name, args in probes:
        ok, stdout, stderr = _run(vbox, *args)
        if ok:
            passed.append(name)
        else:
            detail = _combined_error(stdout, stderr)
            failures.append({
                "probe": name,
                "command": "VBoxManage " + " ".join(args),
                "error": detail or f"VBoxManage {' '.join(args)} failed.",
            })

    combined = "\n".join(item["error"] for item in failures)
    return {
        "ok": not failures,
        "passed": passed,
        "failures": failures,
        "classification": "virtualbox-com-session" if _is_com_lock_error(combined) else "unknown",
    }


def _process_snapshot() -> dict[str, Any]:
    names = ("VBoxSVC.exe", "VirtualBox.exe", "VBoxHeadless.exe", "VBoxManage.exe")
    result: dict[str, Any] = {}

    for name in names:
        try:
            completed = subprocess.run(
                ["tasklist.exe", "/FI", f"IMAGENAME eq {name}", "/FO", "CSV", "/NH"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=10,
                check=False,
            )
            lines = [
                line.strip()
                for line in completed.stdout.splitlines()
                if line.strip() and "INFO:" not in line.upper()
            ]
            result[name] = {"running": bool(lines), "entries": lines}
        except (OSError, subprocess.SubprocessError) as exc:
            result[name] = {"running": False, "error": str(exc)}

    return result


def _repair_vboxsvc(vbox: str) -> dict[str, Any]:
    running_ok, running_vms, running_error = _running_vms(vbox)
    if not running_ok:
        return {
            "attempted": False,
            "success": False,
            "stage": "safety-check",
            "reason": f"Could not verify running VMs; repair aborted: {running_error}",
        }

    if running_vms:
        return {
            "attempted": False,
            "success": False,
            "stage": "safety-check",
            "reason": "Repair skipped because VirtualBox VMs are currently running.",
            "running_vms": running_vms,
        }

    process_before = _process_snapshot()

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

    result = {
        "attempted": True,
        "success": ok,
        "stage": "restart-vboxsvc",
        "action": "restart_vboxsvc",
        "taskkill_returncode": taskkill.returncode,
        "taskkill_error": _combined_error(taskkill.stdout, taskkill.stderr) or None,
        "processes_before": process_before,
        "verification_error": detail if not ok else None,
        "message": (
            "VBoxSVC was restarted and VBoxManage recovered."
            if ok
            else "VBoxSVC restart was attempted, but VBoxManage is still unhealthy."
        ),
    }
    _record("repair-stage", stage="restart-vboxsvc", result=result)
    return result


def _windows_event_correlation() -> dict[str, Any]:
    script = (
        "$start=(Get-Date).AddMinutes(-15); "
        "Get-WinEvent -FilterHashtable @{LogName=@('System','Application');StartTime=$start} "
        "-ErrorAction SilentlyContinue | "
        "Where-Object {$_.ProviderName -match 'VirtualBox|VBox|Service Control Manager'} | "
        "Select-Object -First 25 TimeCreated,ProviderName,Id,LevelDisplayName,Message | "
        "ConvertTo-Json -Depth 3 -Compress"
    )
    try:
        result = subprocess.run(
            ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", script],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=20,
            check=False,
        )
        if result.returncode != 0:
            return {"available": False, "error": _combined_error(result.stdout, result.stderr)}
        raw = result.stdout.strip()
        if not raw:
            return {"available": True, "events": []}
        payload = json.loads(raw)
        events = payload if isinstance(payload, list) else [payload]
        return {"available": True, "events": events}
    except (OSError, subprocess.SubprocessError, json.JSONDecodeError) as exc:
        return {"available": False, "error": str(exc)}


def _recovery_recommendation(probe: dict[str, Any], repair: dict[str, Any] | None = None) -> dict[str, Any]:
    detail = "\n".join(item["error"] for item in probe.get("failures", []))
    if "E_ACCESSDENIED" in detail or "SessionMachine" in detail or "VBoxSVC" in detail:
        return {
            "priority": "high",
            "action": "Restart VBoxSVC only when no VMs are running; otherwise stop affected VMs cleanly first.",
            "reason": "The failure matches a VirtualBox COM/session-lock condition.",
        }
    if repair and not repair.get("success"):
        return {
            "priority": "critical",
            "action": "Manual host-level VirtualBox investigation required.",
            "reason": "The safe VBoxSVC recovery boundary did not restore VBoxManage.",
        }
    return {
        "priority": "medium",
        "action": "Review the failed VBoxManage probe and VirtualBox host state.",
        "reason": "The telemetry engine detected an unclassified VirtualBox failure.",
    }


def _issue_engine(probe: dict[str, Any], vbox: str) -> dict[str, Any]:
    """Classify a telemetry incident and select the safest automatic fixer."""
    detail = "\n".join(item.get("error", "") for item in probe.get("failures", []))
    lowered = detail.lower()

    if _is_com_lock_error(detail):
        issue = "com-session-lock"
        fixer = "restart-vboxsvc"
        safety = "only-when-no-vms-are-running"
        description = "VirtualBox COM/session state is inconsistent or locked."
    elif "not found" in lowered or "cannot find" in lowered:
        issue = "virtualbox-executable"
        fixer = "rediscover-vboxmanage"
        safety = "read-only"
        description = "VBoxManage could not be located."
    elif "timeout" in lowered or "timed out" in lowered:
        issue = "virtualbox-timeout"
        fixer = "restart-vboxsvc"
        safety = "only-when-no-vms-are-running"
        description = "VBoxManage did not respond within the telemetry timeout."
    else:
        issue = "unknown-virtualbox-failure"
        fixer = "diagnose-only"
        safety = "no-destructive-action"
        description = "The failure is not recognized as a safe autonomous repair case."

    return {
        "issue": issue,
        "description": description,
        "fixer": fixer,
        "safety": safety,
        "automatic": fixer != "diagnose-only",
        "vboxmanage": vbox,
    }


def _run_issue_fixer(issue: dict[str, Any], vbox: str) -> dict[str, Any]:
    """Execute only fixers explicitly approved by the issue engine."""
    fixer = issue.get("fixer")

    if fixer == "restart-vboxsvc":
        return _repair_vboxsvc(vbox)

    if fixer == "rediscover-vboxmanage":
        return {
            "attempted": False,
            "success": _find_vboxmanage() is not None,
            "stage": "rediscovery",
            "message": "VBoxManage discovery was retried without changing VirtualBox state.",
        }

    return {
        "attempted": False,
        "success": False,
        "stage": "diagnosis",
        "message": "No autonomous fixer is approved for this issue classification.",
    }


def _repair(force_repair: bool = False) -> dict[str, Any]:
    vbox = _find_vboxmanage()
    if not vbox:
        return {"attempted": False, "success": False, "stage": "discovery", "reason": "VBoxManage.exe not found."}

    repair = _repair_vboxsvc(vbox)
    if repair["success"]:
        return repair

    return {
        **repair,
        "escalation": {
            "level": "manual",
            "reason": (
                "Automatic recovery stopped at the safe VBoxSVC restart boundary. "
                "No VM processes were terminated and no VirtualBox configuration was deleted."
            ),
        },
    }


def check_and_recover(force_repair: bool = False) -> dict[str, Any]:
    now = _now()

    with _lock:
        vbox = _find_vboxmanage()
        if not vbox:
            _state.update({
                "status": "failed",
                "healthy": False,
                "last_check": now,
                "last_error": "VBoxManage.exe not found.",
                "active_incident": True,
            })
            _record("failure", reason="VBoxManage.exe not found")
            return _snapshot()

        probe = _probe(vbox)
        if probe["ok"]:
            was_incident = bool(_state["active_incident"])
            _state.update({
                "status": "recovered" if was_incident else "healthy",
                "healthy": True,
                "consecutive_failures": 0,
                "last_check": now,
                "last_error": None,
                "active_incident": False,
            })
            if was_incident:
                _record("recovered", message="VirtualBox probes returned to healthy state.")
            return _snapshot(
                probe=probe,
                vboxmanage=vbox,
                recommendation=_recovery_recommendation(probe),
            )

        _state["consecutive_failures"] = int(_state["consecutive_failures"]) + 1
        _state.update({
            "last_check": now,
            "healthy": False,
            "status": "degraded",
            "last_error": probe["failures"],
            "active_incident": True,
        })

        _record(
            "probe-failure",
            classification=probe["classification"],
            consecutive_failures=_state["consecutive_failures"],
            failures=probe["failures"],
        )

        issue = _issue_engine(probe, vbox)
        _state["active_issue"] = issue

        should_repair = force_repair or (issue["automatic"] and int(_state["consecutive_failures"]) >= REPAIR_THRESHOLD)

        if _state["last_repair"] and not force_repair:
            try:
                last_repair = datetime.fromisoformat(str(_state["last_repair"]).replace("Z", "+00:00"))
                elapsed = (datetime.now(timezone.utc) - last_repair).total_seconds()
                if elapsed < REPAIR_COOLDOWN_SECONDS:
                    should_repair = False
            except ValueError:
                pass

        if not should_repair:
            result = _snapshot(
                probe=probe,
                vboxmanage=vbox,
                repair_pending=_is_com_lock_error(
                    "\n".join(item["error"] for item in probe["failures"])
                ),
            )
            return result

        repair = _run_issue_fixer(issue, vbox)
        _state["last_repair"] = now
        _state["last_repair_result"] = repair
        _state["repair_count"] = int(_state["repair_count"]) + 1

        verification = _probe(vbox)
        if verification["ok"]:
            _state.update({
                "status": "repaired",
                "healthy": True,
                "consecutive_failures": 0,
                "last_error": None,
                "active_incident": False,
            })
            _record("repaired", repair=repair)
        else:
            _state.update({
                "status": "failed",
                "healthy": False,
                "last_error": verification["failures"],
            })
            correlation = _windows_event_correlation()
            recommendation = _recovery_recommendation(verification, repair)
            repair["windows_event_correlation"] = correlation
            repair["recommendation"] = recommendation
            _record(
                "repair-failed",
                repair=repair,
                verification=verification,
                recommendation=recommendation,
            )

        return _snapshot(
            probe=verification,
            repair=repair,
            vboxmanage=vbox,
        )


def _snapshot(**extra: Any) -> dict[str, Any]:
    return {
        **_state,
        "history": list(_history),
        "persistent_history": persistent_history()[:MAX_HISTORY],
        "incident_log_path": incident_log_path(),
        "policy": {
            "monitor_interval_seconds": MONITOR_INTERVAL_SECONDS,
            "repair_threshold": REPAIR_THRESHOLD,
            "repair_cooldown_seconds": REPAIR_COOLDOWN_SECONDS,
            "probe_timeout_seconds": PROBE_TIMEOUT_SECONDS,
            "max_history": MAX_HISTORY,
        },
        "processes": _process_snapshot(),
        **extra,
    }


def get_telemetry() -> dict[str, Any]:
    return check_and_recover(force_repair=False)


def force_repair() -> dict[str, Any]:
    return check_and_recover(force_repair=True)


def start_monitor() -> None:
    with _lock:
        if _state["monitor_running"]:
            return
        _state["monitor_running"] = True
        _record("monitor-started", interval_seconds=MONITOR_INTERVAL_SECONDS)

    def _loop() -> None:
        while True:
            try:
                check_and_recover()
            except Exception as exc:
                with _lock:
                    _state["status"] = "failed"
                    _state["healthy"] = False
                    _state["last_error"] = str(exc)
                    _state["active_incident"] = True
                    _record("monitor-exception", error=str(exc))
            time.sleep(max(10, MONITOR_INTERVAL_SECONDS))

    thread = threading.Thread(
        target=_loop,
        name="NetworkLab-VBoxTelemetry",
        daemon=True,
    )
    thread.start()
