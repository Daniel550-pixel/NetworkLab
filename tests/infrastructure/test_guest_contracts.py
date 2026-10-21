from app.services.guest_contract_service import get_guest_contracts

def test_guest_contracts_cover_all_roles():
    payload = get_guest_contracts()
    assert {item["role"] for item in payload["contracts"]} == {"MGMT", "INFRA", "CLIENT"}
    assert all(item["os_agnostic"] for item in payload["contracts"])
    assert payload["os_selection"] == "manual"
