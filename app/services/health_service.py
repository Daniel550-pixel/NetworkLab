from app.core.powershell import run_powershell_json

SCRIPT = "powershell/diagnostics/Get-NetworkLabWebHealth.ps1"


def get_health() -> dict:
    return run_powershell_json(SCRIPT)
