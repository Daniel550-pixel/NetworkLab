from app.services import lab_evidence_service as service

def test_evidence_capture_writes_json(monkeypatch, tmp_path):
    monkeypatch.setattr(service, "EVIDENCE_DIR", tmp_path)
    monkeypatch.setattr(service, "get_lab_state", lambda: {"lab": "NetworkLab-Lab"})
    monkeypatch.setattr(service, "verify_lab", lambda: {"verified": False})
    monkeypatch.setattr(service, "get_guest_contracts", lambda: {"contracts": []})
    monkeypatch.setattr(service, "validate_lab_connectivity", lambda: {"pairs": []})
    monkeypatch.setattr(service, "get_telemetry", lambda: {"healthy": True})
    result = service.capture_lab_evidence()
    assert result["captured"] is True
    assert tmp_path.joinpath(result["path"].split("\\")[-1]).exists() or tmp_path.joinpath(result["path"].split("/")[-1]).exists()
