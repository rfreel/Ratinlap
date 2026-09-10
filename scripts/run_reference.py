from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime.scenarios import run_scenarios


def main() -> int:
    report = run_scenarios()
    out = ROOT / "runtime" / "reference-report.json"
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    for row in report["scenarios"]:
        suffix = f" — {row.get('error')}" if row["status"] == "FAIL" else ""
        print(f"{row['status']:4} {row['id']}{suffix}")
    summary = report["summary"]
    print(
        f"{report['status']}: {summary['passed']} scenarios passed, "
        f"{summary['failed']} failed, scopes {summary['covered_scopes']}/{summary['required_scopes']}"
    )
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
