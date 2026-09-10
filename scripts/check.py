from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

REQUIRED_PATHS = (
    "AGENTS.md", "README.md", ".gitignore",
    "contracts/SCOPE.md", "contracts/SEMANTICS.md", "contracts/EVIDENCE.md",
    "contracts/ACCEPTANCE.md", "contracts/CHANGE.md",
    "tasks/QUEUE.jsonl", "tasks/README.md",
    "sources/manifest.json", "sources/README.md",
    "model/model.json", "model/unknowns.jsonl", "model/README.md",
    "observations/README.md", "probes/README.md", "reconstructions/README.md",
    "docs/PREWALK.md",
)
ALLOWED_TASK_STATES = {"READY", "ACTIVE", "DONE", "BLOCKED", "UNKNOWN"}
ALLOWED_EVIDENCE_STATES = {"OFFICIAL", "OBSERVED", "RECONSTRUCTED", "INFERRED", "UNKNOWN"}
ALLOWED_SCOPE_STATES = {"REQUIRED", "OPTIONAL", "EXCLUDED"}
ALLOWED_COVERAGE_STATES = {"COVERED", "PARTIAL", "UNKNOWN"}
SCOPE_RE = re.compile(r"^- (S\d+) \| (REQUIRED|OPTIONAL|EXCLUDED) \| ")
MODEL_KEYS = {
    "schema_version", "status", "primitives", "concepts", "relations",
    "operations", "states", "invariants", "coverage", "acceptance",
}
SOURCE_KEYS = {
    "locator", "role", "revision", "license", "status", "derived_from",
    "independence_group",
}
TASK_KEYS = {
    "id", "state", "depends_on", "artifact", "deliverable", "done_when",
    "scope_ids", "owner",
}


def _load_json(path: Path, label: str, errors: list[str]) -> Any | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    except json.JSONDecodeError as exc:
        errors.append(f"{label}: invalid JSON: {exc.msg} at line {exc.lineno}")
        return None


def _load_jsonl(path: Path, label: str, errors: list[str]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return rows
    for lineno, raw in enumerate(lines, 1):
        if not raw.strip():
            continue
        try:
            value = json.loads(raw)
        except json.JSONDecodeError as exc:
            errors.append(f"{label}:{lineno}: invalid JSON: {exc.msg}")
            continue
        if not isinstance(value, dict):
            errors.append(f"{label}:{lineno}: JSONL row must be an object")
            continue
        rows.append(value)
    return rows


def _scope_declarations(root: Path, errors: list[str]) -> dict[str, str]:
    path = root / "contracts/SCOPE.md"
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return {}
    scopes: dict[str, str] = {}
    for line in lines:
        match = SCOPE_RE.match(line)
        if not match:
            continue
        scope_id, state = match.groups()
        if state not in ALLOWED_SCOPE_STATES:
            errors.append(f"scope {scope_id} has invalid state {state}")
            continue
        if scope_id in scopes:
            errors.append(f"duplicate scope id: {scope_id}")
        scopes[scope_id] = state
    if not scopes:
        errors.append("contracts/SCOPE.md declares no machine-readable scope IDs")
    return scopes


def validate_repo(root: Path) -> list[str]:
    """Return structural validation errors; [] means PASS."""
    root = root.resolve()
    errors: list[str] = []

    for rel in REQUIRED_PATHS:
        if not (root / rel).exists():
            errors.append(f"missing required path: {rel}")

    scopes = _scope_declarations(root, errors)
    declared_scope_ids = set(scopes)
    required_scope_ids = {sid for sid, state in scopes.items() if state == "REQUIRED"}

    tasks = _load_jsonl(root / "tasks/QUEUE.jsonl", "tasks/QUEUE.jsonl", errors)
    task_ids: set[str] = set()
    artifact_owner: dict[str, str] = {}
    for task in tasks:
        missing = TASK_KEYS - set(task)
        if missing:
            errors.append(f"task {task.get('id', '<unknown>')} missing fields: {', '.join(sorted(missing))}")
        task_id = task.get("id")
        if not isinstance(task_id, str):
            errors.append("task id must be a string")
            continue
        if task_id in task_ids:
            errors.append(f"duplicate task id: {task_id}")
        task_ids.add(task_id)
        state = task.get("state")
        if state not in ALLOWED_TASK_STATES:
            errors.append(f"task {task_id} has invalid state {state}")
        if state == "ACTIVE" and not task.get("owner"):
            errors.append(f"ACTIVE task {task_id} has no owner")
        artifact = task.get("artifact")
        if isinstance(artifact, str) and artifact:
            prior = artifact_owner.get(artifact)
            if prior is not None and prior != task_id:
                errors.append(f"tasks {prior} and {task_id} share artifact path {artifact}")
            artifact_owner[artifact] = task_id
            if state == "DONE" and not (root / artifact).exists():
                errors.append(f"DONE task {task_id} missing artifact {artifact}")
        else:
            errors.append(f"task {task_id} has invalid artifact path")
        for scope_id in task.get("scope_ids", []):
            if scope_id not in declared_scope_ids:
                errors.append(f"task {task_id} references undeclared scope id {scope_id}")

    for task in tasks:
        task_id = task.get("id", "<unknown>")
        deps = task.get("depends_on", [])
        if not isinstance(deps, list):
            errors.append(f"task {task_id} depends_on must be a list")
            continue
        for dep in deps:
            if dep not in task_ids:
                errors.append(f"task {task_id} has unknown dependency {dep}")

    model = _load_json(root / "model/model.json", "model/model.json", errors)
    if isinstance(model, dict):
        missing = MODEL_KEYS - set(model)
        if missing:
            errors.append(f"model/model.json missing keys: {', '.join(sorted(missing))}")
        coverage = model.get("coverage", [])
        seen_coverage: set[str] = set()
        if not isinstance(coverage, list):
            errors.append("model/model.json coverage must be a list")
            coverage = []
        for item in coverage:
            if not isinstance(item, dict):
                errors.append("model coverage entry must be an object")
                continue
            scope_id = item.get("scope_id")
            state = item.get("status")
            if scope_id in seen_coverage:
                errors.append(f"duplicate model coverage scope: {scope_id}")
            if isinstance(scope_id, str):
                seen_coverage.add(scope_id)
            if state not in ALLOWED_COVERAGE_STATES:
                errors.append(f"model coverage {scope_id} has invalid status {state}")
        for scope_id in sorted(required_scope_ids - seen_coverage):
            errors.append(f"REQUIRED scope {scope_id} missing from model coverage")

        acceptance = model.get("acceptance", {})
        if not isinstance(acceptance, dict):
            errors.append("model acceptance must be an object")
        elif acceptance.get("high_level_ready") is True:
            if acceptance.get("rival_model_checked") is not True:
                errors.append("high_level_ready requires rival_model_checked=true")
            if acceptance.get("opposite_outcome_checks_complete") is not True:
                errors.append("high_level_ready requires opposite_outcome_checks_complete=true")

    sources = _load_json(root / "sources/manifest.json", "sources/manifest.json", errors)
    if isinstance(sources, list):
        for index, source in enumerate(sources):
            if not isinstance(source, dict):
                errors.append(f"source[{index}] must be an object")
                continue
            missing = SOURCE_KEYS - set(source)
            if missing:
                errors.append(f"source[{index}] missing fields: {', '.join(sorted(missing))}")
            if source.get("status") not in ALLOWED_EVIDENCE_STATES:
                errors.append(f"source[{index}] has invalid evidence status {source.get('status')}")
            if not source.get("independence_group"):
                errors.append(f"source[{index}] has empty independence_group")
            if not isinstance(source.get("derived_from", []), list):
                errors.append(f"source[{index}] derived_from must be a list")
    elif sources is not None:
        errors.append("sources/manifest.json must contain a JSON array")

    unknowns = _load_jsonl(root / "model/unknowns.jsonl", "model/unknowns.jsonl", errors)
    for unknown in unknowns:
        unknown_id = unknown.get("id", "<unknown>")
        evidence_state = unknown.get("evidence_state")
        if evidence_state is not None and evidence_state not in ALLOWED_EVIDENCE_STATES:
            errors.append(f"unknown {unknown_id} has invalid evidence_state {evidence_state}")
        for scope_id in unknown.get("scope_ids", []):
            if scope_id not in declared_scope_ids:
                errors.append(f"unknown {unknown_id} references undeclared scope id {scope_id}")

    return errors


if __name__ == "__main__":
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    errors = validate_repo(root)
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        raise SystemExit(1)
    print("PASS: repository structure valid")
