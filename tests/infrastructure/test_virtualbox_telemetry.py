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
