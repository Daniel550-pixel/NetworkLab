from app.services import inter_vm_validation_service as service

def test_connectivity_matrix_contains_all_directional_pairs(monkeypatch):
    monkeypatch.setattr(service, "_ping", lambda ip: {"reachable": False, "method": "icmp"})
    monkeypatch.setattr(service, "_tcp", lambda ip, port: {"reachable": False, "port": port, "method": "tcp"})
    payload = service.validate_lab_connectivity()
    assert len(payload["pairs"]) == 6
    assert all(pair["status"] == "host-probe-only" for pair in payload["pairs"])
