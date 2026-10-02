from app.services import architecture_service

def test_architecture_exposes_complete_control_pipeline(monkeypatch):
    monkeypatch.setattr(architecture_service, "get_lab_readiness", lambda: {"ready": True})
    monkeypatch.setattr(architecture_service, "get_telemetry", lambda: {
        "healthy": True, "status": "healthy", "active_issue": None, "repair_count": 0
    })
    monkeypatch.setattr(architecture_service, "get_virtual_network", lambda: {
        "ready": True, "name": "NetworkLab-Lab"
    })
    monkeypatch.setattr(architecture_service, "get_vm_topology", lambda: {
        "available": True, "vms": []
    })
    state = architecture_service.get_architecture_state()
    assert state["mode"] == "stage-lab"
    assert len(state["layers"]) == 8
    assert state["pipeline"][-1] == "report"
    assert all(layer["status"] == "ready" for layer in state["layers"])

def test_architecture_keeps_recovery_bounded(monkeypatch):
    monkeypatch.setattr(architecture_service, "get_lab_readiness", lambda: {"ready": False})
    monkeypatch.setattr(architecture_service, "get_telemetry", lambda: {
        "healthy": False, "status": "failed", "active_issue": "unknown", "repair_count": 1
    })
    monkeypatch.setattr(architecture_service, "get_virtual_network", lambda: {"ready": False})
    monkeypatch.setattr(architecture_service, "get_vm_topology", lambda: {"available": False})
    state = architecture_service.get_architecture_state()
    assert state["layers"][1]["status"] == "attention"
    assert state["layers"][5]["status"] == "attention"
