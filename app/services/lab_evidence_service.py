from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import json

from app.services.guest_contract_service import get_guest_contracts
from app.services.inter_vm_validation_service import validate_lab_connectivity
from app.services.lab_lifecycle_service import get_lab_state
from app.services.verification_service import verify_lab
from app.services.virtualbox_telemetry_service import get_telemetry

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_DIR = ROOT / "logs" / "evidence"

def capture_lab_evidence() -> dict:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "lab": get_lab_state(),
        "verification": verify_lab(),
        "guest_contracts": get_guest_contracts(),
        "connectivity": validate_lab_connectivity(),
        "telemetry": get_telemetry(),
    }
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = EVIDENCE_DIR / f"networklab-{stamp}.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    return {"captured": True, "path": str(path), "payload": payload}
