from app.services.lab_definition import VM_ROLES
from app.services import lab_lifecycle_service

def test_lab_definition_has_three_explicit_roles():
    assert [item["role"] for item in VM_ROLES] == ["MGMT", "INFRA", "CLIENT"]
    assert [item["recommended_ip"] for item in VM_ROLES] == [
        "192.168.77.10", "192.168.77.20", "192.168.77.30"
    ]

def test_lab_state_contains_all_host_layers(monkeypatch):
    monkeypatch.setattr(lab_lifecycle_service, "get_virtual_network", lambda: {"ready": True})
    monkeypatch.setattr(lab_lifecycle_service, "get_vm_topology", lambda: {"vms": []})
    monkeypatch.setattr(lab_lifecycle_service, "get_vm_storage", lambda: {"vms": []})
    monkeypatch.setattr(lab_lifecycle_service, "get_lab_readiness", lambda: {"ready": False})
    state = lab_lifecycle_service.get_lab_state()
    assert {"definition", "network", "topology", "storage", "readiness"} <= set(state)
