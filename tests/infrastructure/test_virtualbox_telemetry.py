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
