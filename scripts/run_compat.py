from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "compat" / "report.json"


def main() -> int:
    command = [sys.executable, "-m", "unittest", "compat.test_server", "-v"]
    completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    combined = (completed.stdout + completed.stderr).strip()
    status = "PASS" if completed.returncode == 0 else "FAIL"
    report = {
        "schema_version": "0.1",
        "target": "API_SLICE_READY",
        "status": status,
        "command": " ".join(command),
        "returncode": completed.returncode,
        "seven_routes_exercised": completed.returncode == 0,
        "output": combined,
    }
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(combined)
    print(f"{status}: wrote {OUT.relative_to(ROOT)}")
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
