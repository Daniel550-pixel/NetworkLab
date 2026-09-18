from app.core.powershell import run_powershell_json

SCRIPT = "powershell/manage/Get-NetworkLabWebEvidence.ps1"


def get_evidence() -> dict:
    return run_powershell_json(SCRIPT)
