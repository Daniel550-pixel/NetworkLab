"""Generate a simple JSON monitoring report from NetworkLab checks."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone


def build_report(results: list[dict[str, object]]) -> dict[str, object]:
    passed = sum(bool(item.get("reachable", item.get("resolved", False))) for item in results)
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_checks": len(results),
        "passed_checks": passed,
        "failed_checks": len(results) - passed,
        "results": results,
    }


if __name__ == "__main__":
    # Accept JSON from stdin so the reporter can be chained to monitoring tools.
    payload = sys.stdin.read().strip()
    results = json.loads(payload) if payload else []
    print(json.dumps(build_report(results), indent=2))
