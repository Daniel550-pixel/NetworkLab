from app.services.virtualbox_telemetry_service import _is_com_lock_error


def test_com_lock_error_is_detected():
    detail = (
        "VBoxManage.exe: error: The object is not ready "
        "Details: code E_ACCESSDENIED (0x80070005), "
        "component SessionMachine"
    )
    assert _is_com_lock_error(detail)


def test_unrelated_error_is_not_classified_as_com_lock():
    assert not _is_com_lock_error("VBoxManage.exe: error: Unknown command")


from app.services.virtualbox_telemetry_service import _recovery_recommendation


def test_com_lock_recovery_recommendation_is_high_priority():
    probe = {"failures": [{"error": "E_ACCESSDENIED SessionMachine"}]}
    recommendation = _recovery_recommendation(probe)
    assert recommendation["priority"] == "high"
    assert "VBoxSVC" in recommendation["action"]


def test_failed_recovery_recommendation_escalates():
    probe = {"failures": [{"error": "still failing"}]}
    recommendation = _recovery_recommendation(probe, {"success": False})
    assert recommendation["priority"] == "critical"


from app.services.virtualbox_telemetry_service import _issue_engine


def test_issue_engine_classifies_com_session_failure():
    probe = {"failures": [{"error": "E_ACCESSDENIED SessionMachine"}]}
    issue = _issue_engine(probe, "VBoxManage.exe")
    assert issue["issue"] == "com-session-lock"
    assert issue["fixer"] == "restart-vboxsvc"
    assert issue["automatic"] is True


def test_issue_engine_does_not_autofix_unknown_failure():
    probe = {"failures": [{"error": "Unknown VirtualBox failure"}]}
    issue = _issue_engine(probe, "VBoxManage.exe")
    assert issue["issue"] == "unknown-virtualbox-failure"
    assert issue["automatic"] is False
    assert issue["fixer"] == "diagnose-only"
