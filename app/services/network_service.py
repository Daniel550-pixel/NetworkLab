from app.core.powershell import run_powershell_json

SCRIPT = "powershell/manage/Get-NetworkLabState.ps1"


def get_state() -> dict:
    return run_powershell_json(SCRIPT)
