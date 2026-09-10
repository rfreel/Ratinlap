# Ratinlap Bootstrap Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Bootstrap `rfreel/Ratinlap` into a minimal, agent-operable reconstruction workspace with explicit contracts, canonical task/model state, source seeds, and a zero-dependency structural validator.

**Architecture:** Keep all project state inspectable in plain files. `model/model.json` and `tasks/QUEUE.jsonl` are the only canonical working-state files; Markdown contracts constrain their meaning, workers write only task artifacts, and a coordinator alone updates canonical state. A Python standard-library validator checks structure and internal consistency but does not claim semantic truth.

**Tech Stack:** Markdown, JSON, JSONL, Python 3 standard library, Git.

**Spec:** `docs/superpowers/specs/2026-09-10-ratinlap-reconstruction-design.md`

## Global Constraints

- No database, graph engine, task service, package manager, or application framework is required for bootstrap.
- `model/model.json` and `tasks/QUEUE.jsonl` are single-writer canonical state.
- Workers never write canonical state directly; only the coordinator integrates canonical changes.
- `UNKNOWN` is never silently promoted to fact.
- Third-party reconstruction agreement is grouped by lineage and does not become `OFFICIAL` evidence.
- `HIGH_LEVEL_READY` is distinct from `BOOTSTRAP_COMPLETE`.
- Every REQUIRED scope item is represented explicitly in model coverage.
- Every DONE task has a repository artifact and a checkable completion condition.
- New infrastructure requires a concrete failure of the existing minimal structure.

## Files created by this plan

```text
AGENTS.md                         root operating contract and cold-start protocol
README.md                         project orientation and current completion states
.gitignore                       local/editor/cache exclusions
contracts/SCOPE.md               stable reconstruction denominator S01-S10
contracts/SEMANTICS.md           candidate semantic vocabulary and primitive rules
contracts/EVIDENCE.md            evidence classes and source-lineage rules
contracts/ACCEPTANCE.md          BOOTSTRAP_COMPLETE / HIGH_LEVEL_READY gates
contracts/CHANGE.md              model/task mutation rules and single-writer policy
tasks/QUEUE.jsonl                canonical task state
tasks/README.md                  task schema, state machine, claiming and handoff rules
sources/manifest.json            seeded official and independent sources
sources/README.md                source acquisition and pinning rules
model/model.json                 canonical reconstructed model shell + coverage
model/unknowns.jsonl             unresolved model-changing questions
model/README.md                  canonical model shape and update discipline
observations/README.md           artifact format for extracted observations
probes/README.md                 discriminator/probe contract
reconstructions/README.md        comparison artifact contract
scripts/check.py                 zero-dependency structural validator
scripts/test_check.py            validator unit tests using tempfile fixtures
docs/PREWALK.md                  outside-in execution route
```

---

### Task 1: Structural validator contract

**Files:**
- Create: `scripts/check.py`
- Create: `scripts/test_check.py`

**Interfaces:**
- Consumes: repository root path, Markdown scope declaration, JSON source/model state, JSONL task/unknown state.
- Produces: `validate_repo(root: Path) -> list[str]`; empty list means structural PASS. CLI exits `0` on PASS and `1` on one or more errors.

- [ ] **Step 1: Write validator tests before implementation**

Create `scripts/test_check.py` with tests for: a complete synthetic repository passes; a missing required file fails; duplicate task IDs fail; unknown task dependencies fail; an ACTIVE task with no owner fails; a DONE task with a missing artifact fails; an undeclared task scope ID fails; a REQUIRED scope missing from model coverage fails; malformed JSON/JSONL fails; and `high_level_ready=true` fails unless rival-model and opposite-outcome checks are true.

Use Python `unittest`, `tempfile.TemporaryDirectory`, and helper functions that create a complete valid fixture tree before each negative mutation.

Run:

```bash
python -m unittest scripts.test_check -v
```

Expected before implementation: import/error because `scripts.check.validate_repo` does not yet exist.

- [ ] **Step 2: Implement the minimal validator**

Create `scripts/check.py` with these constants and public function:

```python
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

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


def validate_repo(root: Path) -> list[str]:
    """Return structural validation errors; [] means PASS."""
    errors: list[str] = []
    # 1. required paths
    # 2. parse scope IDs from contracts/SCOPE.md
    # 3. parse tasks/QUEUE.jsonl, enforce unique IDs/state/dependencies/owner/artifact/scope IDs
    # 4. parse model/model.json and validate required top-level keys
    # 5. ensure all REQUIRED scope IDs appear in model.coverage
    # 6. parse sources/manifest.json and require locator/role/revision/license/status/derived_from/independence_group
    # 7. parse model/unknowns.jsonl and validate evidence_state when present
    # 8. if acceptance.high_level_ready is true require rival_model_checked and opposite_outcome_checks_complete
    return errors
```

Fill those eight checks directly; do not add dependencies or abstraction layers. Required `model.json` keys are exactly:

```text
schema_version
status
primitives
concepts
relations
operations
states
invariants
coverage
acceptance
```

For CLI behavior:

```python
if __name__ == "__main__":
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    errors = validate_repo(root)
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        raise SystemExit(1)
    print("PASS: repository structure valid")
```

- [ ] **Step 3: Run validator unit tests**

Run:

```bash
python -m unittest scripts.test_check -v
```

Expected: all tests PASS.

- [ ] **Step 4: Commit**

```bash
git add scripts/check.py scripts/test_check.py
git commit -m "test: define bootstrap structural validator"
```

---

### Task 2: Root authority and reconstruction contracts

**Files:**
- Create: `AGENTS.md`
- Create: `README.md`
- Create: `.gitignore`
- Create: `contracts/SCOPE.md`
- Create: `contracts/SEMANTICS.md`
- Create: `contracts/EVIDENCE.md`
- Create: `contracts/ACCEPTANCE.md`
- Create: `contracts/CHANGE.md`

**Interfaces:**
- Consumes: approved design spec.
- Produces: human/agent-readable invariants used by every later task and parsed scope IDs `S01` through `S10`.

- [ ] **Step 1: Create `AGENTS.md`**

It must contain, in this order: Purpose; Cold Start; Roles; Hard Rules; Task Execution; Model Changes; External Actions; Completion. Hard rules are the 16 approved rules from the design, including prior-art-first search, no UNKNOWN promotion, lineage-aware evidence, explicit denominator, primitive ablation, single-writer canonical state, checkable DONE artifacts, and opposite-outcome testing for decision-changing unknowns.

Cold start must be exactly:

```text
1. Read AGENTS.md.
2. Read contracts/SCOPE.md, contracts/SEMANTICS.md, contracts/ACCEPTANCE.md.
3. Read tasks/QUEUE.jsonl.
4. Read only source/model files named by the selected task.
5. Execute one task to its artifact and completion condition.
```

- [ ] **Step 2: Create the finite scope denominator**

`contracts/SCOPE.md` must declare these exact machine-readable lines:

```text
- S01 | REQUIRED | ontology identity and type-instance split
- S02 | REQUIRED | objects and properties
- S03 | REQUIRED | links and linked-object traversal
- S04 | REQUIRED | ObjectSet query filter and aggregation semantics
- S05 | REQUIRED | actions validation effects and visible failure states
- S06 | REQUIRED | functions and derived values where publicly exposed
- S07 | REQUIRED | authentication and authorization boundaries
- S08 | REQUIRED | asynchronous loading and event behavior where publicly exposed
- S09 | REQUIRED | OSDK versus Platform API boundary
- S10 | REQUIRED | application-facing interaction boundary
```

Also state that changes to REQUIRED/OPTIONAL/EXCLUDED classification are explicit scope changes.

- [ ] **Step 3: Create semantic, evidence, acceptance and change contracts**

`contracts/SEMANTICS.md` defines `THING`, `RELATION`, `TRANSITION`, `QUERY`, `POLICY`, `EVENT` as candidate primitives, not truths; requires ablation/merge testing before accepting a primitive as necessary; and forbids forcing observably distinct behavior into one primitive merely to keep the vocabulary small.

`contracts/EVIDENCE.md` defines exactly `OFFICIAL`, `OBSERVED`, `RECONSTRUCTED`, `INFERRED`, `UNKNOWN`; states that `RECONSTRUCTED` consensus never becomes `OFFICIAL`; and requires `derived_from` plus `independence_group` on reconstruction sources.

`contracts/ACCEPTANCE.md` defines both gates:

```text
BOOTSTRAP_COMPLETE = structure exists + contracts populated + queue valid + source seeds recorded + model parses + scripts/check.py PASS
HIGH_LEVEL_READY = all approved semantic acceptance bullets in the design spec pass
```

`contracts/CHANGE.md` names `model/model.json` and `tasks/QUEUE.jsonl` as single-writer coordinator surfaces and requires every model-changing task to name the scope IDs and distinction it may alter.

- [ ] **Step 4: Create root orientation files**

`README.md` must identify the project as a public/observable reconstruction workspace, point first-time agents to `AGENTS.md`, distinguish `BOOTSTRAP_COMPLETE` from `HIGH_LEVEL_READY`, and link the spec and plan paths.

`.gitignore` contains only:

```text
__pycache__/
*.py[cod]
.DS_Store
.venv/
.env
```

- [ ] **Step 5: Validate the contract surface**

Run:

```bash
python - <<'PY'
from pathlib import Path
required = ["AGENTS.md", "README.md", ".gitignore", "contracts/SCOPE.md", "contracts/SEMANTICS.md", "contracts/EVIDENCE.md", "contracts/ACCEPTANCE.md", "contracts/CHANGE.md"]
missing = [p for p in required if not Path(p).exists()]
assert not missing, missing
scope = Path("contracts/SCOPE.md").read_text()
for i in range(1, 11):
    assert f"S{i:02d}" in scope
print("PASS: root contracts")
PY
```

Expected: `PASS: root contracts`.

- [ ] **Step 6: Commit**

```bash
git add AGENTS.md README.md .gitignore contracts
git commit -m "docs: establish reconstruction contracts"
```

---

### Task 3: Canonical model and source seeds

**Files:**
- Create: `sources/manifest.json`
- Create: `sources/README.md`
- Create: `model/model.json`
- Create: `model/unknowns.jsonl`
- Create: `model/README.md`

**Interfaces:**
- Consumes: `contracts/SCOPE.md`, `contracts/EVIDENCE.md`.
- Produces: canonical model shell, explicit coverage for S01-S10, and lineage-aware source seeds.

- [ ] **Step 1: Create source manifest**

`sources/manifest.json` is a JSON array with these seven seeds:

```text
palantir/osdk-ts                         official
palantir/foundry-platform-typescript     official
palantir/ontology-starter-react-app      official
palantir/workshop-iframe-custom-widget   official
gura105/operational-ontology             third_party
Przyval/openfoundry                      third_party
syzygyhack/open-foundry                  third_party
```

Every object has exactly these fields initially:

```json
{
  "locator": "owner/repo",
  "role": "official_sdk_or_reference",
  "revision": "UNPINNED",
  "license": "UNVERIFIED",
  "status": "OFFICIAL",
  "derived_from": [],
  "independence_group": "official-palantir"
}
```

Use `status:"RECONSTRUCTED"` and a distinct independence-group string for each of the three independent reconstruction seeds. `role` should distinguish `official_sdk`, `official_reference_app`, `official_integration`, `minimal_reference_reconstruction`, `foundry_api_emulator`, and `independent_operational_platform` as appropriate.

- [ ] **Step 2: Create canonical model shell**

`model/model.json` starts with:

```json
{
  "schema_version": "0.1",
  "status": "BOOTSTRAP",
  "primitives": ["THING", "RELATION", "TRANSITION", "QUERY", "POLICY", "EVENT"],
  "concepts": [],
  "relations": [],
  "operations": [],
  "states": [],
  "invariants": [],
  "coverage": [
    {"scope_id":"S01","status":"UNKNOWN"},
    {"scope_id":"S02","status":"UNKNOWN"},
    {"scope_id":"S03","status":"UNKNOWN"},
    {"scope_id":"S04","status":"UNKNOWN"},
    {"scope_id":"S05","status":"UNKNOWN"},
    {"scope_id":"S06","status":"UNKNOWN"},
    {"scope_id":"S07","status":"UNKNOWN"},
    {"scope_id":"S08","status":"UNKNOWN"},
    {"scope_id":"S09","status":"UNKNOWN"},
    {"scope_id":"S10","status":"UNKNOWN"}
  ],
  "acceptance": {
    "bootstrap_complete": false,
    "high_level_ready": false,
    "rival_model_checked": false,
    "opposite_outcome_checks_complete": false
  }
}
```

This is a candidate-model shell only; no Palantir-specific semantic claim is populated during bootstrap.

- [ ] **Step 3: Seed explicit unknowns**

Create `model/unknowns.jsonl` with one record establishing that the candidate primitive set itself remains falsifiable:

```json
{"id":"U001","scope_ids":["S01","S03","S05","S09"],"question":"Does the candidate primitive set preserve every REQUIRED observable distinction, or does a rival representation require a different primitive boundary?","evidence_state":"UNKNOWN","decision_changing":true,"discriminator":"Fit at least one materially different rival representation to the same REQUIRED observations and run primitive ablation/merge tests.","status":"OPEN"}
```

- [ ] **Step 4: Document source/model update rules**

`sources/README.md` says seeds are not the corpus, revisions/licenses must be pinned before being used as evidence, prior-art discovery uses materially different search families, and two no-new-distinction search families form only a saturation heuristic.

`model/README.md` states that workers propose changes but only the coordinator edits `model/model.json`; every accepted model change names affected scope IDs, evidence class, and the distinction gained/lost.

- [ ] **Step 5: Validate JSON and coverage**

Run:

```bash
python - <<'PY'
import json
from pathlib import Path
sources = json.loads(Path("sources/manifest.json").read_text())
model = json.loads(Path("model/model.json").read_text())
assert len(sources) == 7
assert {x["scope_id"] for x in model["coverage"]} == {f"S{i:02d}" for i in range(1,11)}
assert model["acceptance"]["high_level_ready"] is False
print("PASS: canonical seeds")
PY
```

Expected: `PASS: canonical seeds`.

- [ ] **Step 6: Commit**

```bash
git add sources model
git commit -m "chore: seed reconstruction model and sources"
```

---

### Task 4: Canonical task management

**Files:**
- Create: `tasks/QUEUE.jsonl`
- Create: `tasks/README.md`

**Interfaces:**
- Consumes: scope IDs S01-S10 and source seed roles.
- Produces: one-current-record-per-task queue with explicit dependencies and disjoint task artifacts.

- [ ] **Step 1: Create the task contract**

`tasks/README.md` defines this state machine:

```text
READY -> ACTIVE -> DONE
             \-> BLOCKED
             \-> UNKNOWN -> READY
```

Rules: ACTIVE requires owner; READY can be claimed only when dependencies are DONE; one current record per ID; queue is rewritten state, not an event log; parallel tasks cannot share artifact paths; DONE requires artifact existence and a repository-checkable `done_when`; BLOCKED names an external dependency/authorization boundary; UNKNOWN names a missing discriminator.

Worker handoff object is exactly:

```json
{"task_id":"T001","artifact":"reconstructions/example.md","observed_distinctions":[],"proposed_model_changes":[],"new_unknowns":[],"done_when_result":"PASS"}
```

- [ ] **Step 2: Create `tasks/QUEUE.jsonl`**

Create 14 READY tasks with unique artifact paths and explicit dependencies:

```text
T001 prior-art discovery and lineage map
T002 inspect gura105/operational-ontology
T003 inspect Przyval/openfoundry
T004 inspect syzygyhack/open-foundry
T005 map official Palantir OSDK/API surface
T006 compute shared observable distinctions
T007 record reconstruction disagreements
T008 construct rival representation
T009 isolate Palantir-specific constraints
T010 compile model/model.json v0
T011 enumerate high-value unknowns
T012 run opposite-outcome checks
T013 design discriminating probes
T014 synthesize high-level architecture
```

Use artifact paths:

```text
reconstructions/prior-art.md
reconstructions/gura105-operational-ontology.md
reconstructions/przyval-openfoundry.md
reconstructions/syzygyhack-open-foundry.md
observations/palantir-public-surface.md
observations/shared-distinctions.md
observations/reconstruction-disagreements.md
model/rival-representation.md
observations/palantir-specific.md
model/model-v0-review.md
model/high-value-unknowns.md
model/opposite-outcomes.md
probes/discriminators.md
docs/HIGH_LEVEL_MODEL.md
```

Dependencies:

```text
T001 []
T002 [T001]
T003 [T001]
T004 [T001]
T005 [T001]
T006 [T002,T003,T004,T005]
T007 [T002,T003,T004,T005]
T008 [T006,T007]
T009 [T005,T006,T007]
T010 [T008,T009]
T011 [T010]
T012 [T011]
T013 [T011,T012]
T014 [T010,T12,T013]
```

Use `T012` rather than `T12` in the actual JSONL dependency list. Every task contains: `id`, `state`, `depends_on`, `artifact`, `deliverable`, `done_when`, `scope_ids`, `owner`. Set all owners to `null`. `scope_ids` must be the smallest relevant subset, except T014 which may include S01-S10.

- [ ] **Step 3: Validate queue semantics**

Run:

```bash
python - <<'PY'
import json
from pathlib import Path
rows=[json.loads(x) for x in Path("tasks/QUEUE.jsonl").read_text().splitlines() if x.strip()]
ids={r["id"] for r in rows}
assert len(rows)==14 and len(ids)==14
for r in rows:
    assert set(r["depends_on"]) <= ids
    assert r["state"] == "READY"
    assert r["owner"] is None
print("PASS: task queue")
PY
```

Expected: `PASS: task queue`.

- [ ] **Step 4: Commit**

```bash
git add tasks
git commit -m "chore: add canonical reconstruction task queue"
```

---

### Task 5: Research artifact contracts and prewalk

**Files:**
- Create: `observations/README.md`
- Create: `probes/README.md`
- Create: `reconstructions/README.md`
- Create: `docs/PREWALK.md`

**Interfaces:**
- Consumes: source/evidence/task contracts.
- Produces: exact artifact formats for source inspection, comparison, and discriminating probes; cold-start execution route.

- [ ] **Step 1: Define reconstruction artifact format**

`reconstructions/README.md` requires each reconstruction review to record: locator, pinned revision, license, independence group, claimed scope, implemented objects/links/actions/query behavior, failure semantics, state authority, observable divergences from official Palantir surface, and proposed model changes. No raw source dump.

- [ ] **Step 2: Define observation format**

`observations/README.md` requires each observation to contain: `scope_id`, statement, evidence state, source locator/revision, smallest supporting witness, counterfactual/opposite if decision-changing, and model consequence.

- [ ] **Step 3: Define probe format**

`probes/README.md` requires: question, rival predictions, minimum authorized input, expected observation under each rival, execution boundary, result, and routing consequence. A probe is run only when its result can change the high-level model or task routing.

- [ ] **Step 4: Write the prewalk**

`docs/PREWALK.md` reproduces the 13-step approved outside-in route: freeze denominator; prior-art discovery + lineage deduplication; source inventory; disjoint worker assignments; extract semantics; compare lineage-distinct reconstructions against official surfaces; compile smallest candidate; rival representation + ablation; preserve disagreements; invert decision-changing unknowns; run only valuable probes; recompute coverage; stop when remaining unknowns cannot alter the core model.

It must end with:

```text
BOOTSTRAP is preparation.
HIGH_LEVEL_READY is a semantic result.
Never report the first as the second.
```

- [ ] **Step 5: Commit**

```bash
git add observations probes reconstructions docs/PREWALK.md
git commit -m "docs: define reconstruction artifact workflow"
```

---

### Task 6: Bootstrap integration and acceptance

**Files:**
- Modify: `model/model.json`
- Test: repository root with `scripts/check.py` and `scripts/test_check.py`

**Interfaces:**
- Consumes: every artifact created in Tasks 1-5.
- Produces: structurally valid repository with `BOOTSTRAP_COMPLETE=true` and `HIGH_LEVEL_READY=false`.

- [ ] **Step 1: Run unit tests**

```bash
python -m unittest scripts.test_check -v
```

Expected: all validator tests PASS.

- [ ] **Step 2: Run repository validator before final state flip**

```bash
python scripts/check.py .
```

Expected: `PASS: repository structure valid`.

- [ ] **Step 3: Set only bootstrap acceptance true**

Change `model/model.json`:

```json
"acceptance": {
  "bootstrap_complete": true,
  "high_level_ready": false,
  "rival_model_checked": false,
  "opposite_outcome_checks_complete": false
}
```

Do not add semantic claims merely to make coverage look better; all S01-S10 remain `UNKNOWN` until research tasks produce witnesses.

- [ ] **Step 4: Re-run all checks**

```bash
python -m unittest scripts.test_check -v
python scripts/check.py .
```

Expected: all unit tests PASS and `PASS: repository structure valid`.

- [ ] **Step 5: Verify cold-start sufficiency**

From repository root, follow only the written cold-start path in `AGENTS.md` and confirm it deterministically selects the next runnable task: `T001`, because it alone has no dependencies. No chat context may be required to determine the artifact, completion condition, or source-search objective.

Expected: `T001` is uniquely runnable at bootstrap.

- [ ] **Step 6: Commit**

```bash
git add model/model.json
git commit -m "chore: mark Ratinlap bootstrap complete"
```

## Plan self-review

Spec coverage mapping:

```text
finite scope denominator                  Task 2 + Task 3
candidate semantic substrate             Task 2 + Task 3
five evidence states + lineage           Task 2 + Task 3
cold-start and coordinator/worker roles  Task 2 + Task 4
task state machine and artifacts         Task 4
bounded prior-art source strategy        Task 3 + Task 5
rival representation requirement         Task 3 + queued T008
opposite-outcome requirement             Task 3 + queued T012
structural validator                     Task 1 + Task 6
bootstrap/high-level separation          Task 2 + Task 6
outside-in prewalk                        Task 5
```

The plan contains no unresolved implementation placeholders. Naming is consistent across the validator, queue, scope IDs, model keys, and acceptance fields. The only semantic fields intentionally left `UNKNOWN` are research results that the approved spec explicitly forbids inventing during bootstrap.