from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.check import validate_repo


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


def write_text(root: Path, path: str, text: str = "ok\n") -> None:
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")


def write_json(root: Path, path: str, value: object) -> None:
    write_text(root, path, json.dumps(value, indent=2) + "\n")


def valid_model() -> dict:
    return {
        "schema_version": "0.1",
        "status": "BOOTSTRAP",
        "primitives": ["THING", "RELATION", "TRANSITION", "QUERY", "POLICY", "EVENT"],
        "concepts": [],
        "relations": [],
        "operations": [],
        "states": [],
        "invariants": [],
        "coverage": [{"scope_id": f"S{i:02d}", "status": "UNKNOWN"} for i in range(1, 11)],
        "acceptance": {
            "bootstrap_complete": False,
            "high_level_ready": False,
            "rival_model_checked": False,
            "opposite_outcome_checks_complete": False,
        },
    }


def valid_sources() -> list[dict]:
    return [
        {
            "locator": "example/repo",
            "role": "reference",
            "revision": "UNPINNED",
            "license": "UNVERIFIED",
            "status": "RECONSTRUCTED",
            "derived_from": [],
            "independence_group": "example",
        }
    ]


def valid_task() -> dict:
    return {
        "id": "T001",
        "state": "READY",
        "depends_on": [],
        "artifact": "reconstructions/prior-art.md",
        "deliverable": "Prior-art inventory",
        "done_when": "Artifact records at least one search family and lineage decision.",
        "scope_ids": ["S01"],
        "owner": None,
    }


def build_valid_repo(root: Path) -> None:
    for path in REQUIRED_PATHS:
        write_text(root, path)
    scope = "# Scope\n\n" + "".join(
        f"- S{i:02d} | REQUIRED | scope {i}\n" for i in range(1, 11)
    )
    write_text(root, "contracts/SCOPE.md", scope)
    write_json(root, "model/model.json", valid_model())
    write_text(
        root,
        "model/unknowns.jsonl",
        json.dumps({
            "id": "U001",
            "scope_ids": ["S01"],
            "question": "Does the candidate model preserve this distinction?",
            "evidence_state": "UNKNOWN",
            "decision_changing": True,
            "discriminator": "Fit a rival representation.",
            "status": "OPEN",
        }) + "\n",
    )
    write_json(root, "sources/manifest.json", valid_sources())
    write_text(root, "tasks/QUEUE.jsonl", json.dumps(valid_task()) + "\n")


class ValidateRepoTests(unittest.TestCase):
    def with_repo(self):
        temp = tempfile.TemporaryDirectory()
        root = Path(temp.name)
        build_valid_repo(root)
        return temp, root

    def test_complete_repository_passes(self):
        temp, root = self.with_repo()
        self.addCleanup(temp.cleanup)
        self.assertEqual(validate_repo(root), [])

    def test_missing_required_file_fails(self):
        temp, root = self.with_repo()
        self.addCleanup(temp.cleanup)
        (root / "AGENTS.md").unlink()
        self.assertTrue(any("missing required path: AGENTS.md" in e for e in validate_repo(root)))

    def test_duplicate_task_ids_fail(self):
        temp, root = self.with_repo()
        self.addCleanup(temp.cleanup)
        task = valid_task()
        write_text(root, "tasks/QUEUE.jsonl", json.dumps(task) + "\n" + json.dumps(task) + "\n")
        self.assertTrue(any("duplicate task id: T001" in e for e in validate_repo(root)))

    def test_unknown_task_dependency_fails(self):
        temp, root = self.with_repo()
        self.addCleanup(temp.cleanup)
        task = valid_task()
        task["depends_on"] = ["T999"]
        write_text(root, "tasks/QUEUE.jsonl", json.dumps(task) + "\n")
        self.assertTrue(any("unknown dependency T999" in e for e in validate_repo(root)))

    def test_active_task_requires_owner(self):
        temp, root = self.with_repo()
        self.addCleanup(temp.cleanup)
        task = valid_task()
        task["state"] = "ACTIVE"
        write_text(root, "tasks/QUEUE.jsonl", json.dumps(task) + "\n")
        self.assertTrue(any("ACTIVE task T001 has no owner" in e for e in validate_repo(root)))

    def test_done_task_requires_artifact(self):
        temp, root = self.with_repo()
        self.addCleanup(temp.cleanup)
        task = valid_task()
        task["state"] = "DONE"
        task["owner"] = "worker-1"
        write_text(root, "tasks/QUEUE.jsonl", json.dumps(task) + "\n")
        self.assertTrue(any("DONE task T001 missing artifact" in e for e in validate_repo(root)))

    def test_task_scope_must_exist(self):
        temp, root = self.with_repo()
        self.addCleanup(temp.cleanup)
        task = valid_task()
        task["scope_ids"] = ["S99"]
        write_text(root, "tasks/QUEUE.jsonl", json.dumps(task) + "\n")
        self.assertTrue(any("undeclared scope id S99" in e for e in validate_repo(root)))

    def test_required_scope_must_have_coverage(self):
        temp, root = self.with_repo()
        self.addCleanup(temp.cleanup)
        model = valid_model()
        model["coverage"] = model["coverage"][:-1]
        write_json(root, "model/model.json", model)
        self.assertTrue(any("REQUIRED scope S10 missing from model coverage" in e for e in validate_repo(root)))

    def test_malformed_json_fails(self):
        temp, root = self.with_repo()
        self.addCleanup(temp.cleanup)
        write_text(root, "sources/manifest.json", "{bad json\n")
        self.assertTrue(any("sources/manifest.json" in e and "invalid JSON" in e for e in validate_repo(root)))

    def test_high_level_ready_requires_meta_checks(self):
        temp, root = self.with_repo()
        self.addCleanup(temp.cleanup)
        model = valid_model()
        model["acceptance"]["high_level_ready"] = True
        write_json(root, "model/model.json", model)
        errors = validate_repo(root)
        self.assertTrue(any("rival_model_checked" in e for e in errors))
        self.assertTrue(any("opposite_outcome_checks_complete" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
