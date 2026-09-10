# Ratinlap reconstruction design

## Purpose

Ratinlap is a compact research-and-reconstruction workspace for understanding the public/observable architecture of Palantir Foundry-style operational ontology systems without pretending to know proprietary internals.

The repository optimizes for fast comprehension, explicit uncertainty, low operational overhead, and easy handoff between chat, coding agents, and human review.

The target is not "understand Foundry" in the abstract. The target is a finite public-surface model whose coverage can be counted and whose remaining unknowns are explicit.

## Scope and denominator

`contracts/SCOPE.md` defines the reconstruction denominator. Every included surface receives a stable scope ID and one state: `REQUIRED`, `OPTIONAL`, or `EXCLUDED`.

The initial REQUIRED surface is:

- ontology identity and type/instance split
- objects and properties
- links and linked-object traversal
- ObjectSet/query/filter/aggregation semantics
- actions, validation, effects, and visible failure states
- functions and derived values where publicly exposed
- authentication and authorization boundaries
- asynchronous/loading/event behavior where publicly exposed
- OSDK versus Platform API boundary
- application-facing interaction boundary

Out of scope unless later promoted:

- proprietary source recovery
- claims about hidden storage/scheduling/runtime internals without public observation
- visual cloning of Palantir applications
- exhaustive compatibility engineering
- enterprise-scale performance equivalence

Coverage is always reported against this explicit denominator. Adding or removing a REQUIRED surface is a scope change, not an unnoticed change in the meaning of "complete."

## Repository structure

```text
Ratinlap/
├── AGENTS.md
├── README.md
├── contracts/
│   ├── SCOPE.md
│   ├── SEMANTICS.md
│   ├── EVIDENCE.md
│   ├── ACCEPTANCE.md
│   └── CHANGE.md
├── tasks/
│   ├── QUEUE.jsonl
│   └── README.md
├── sources/
│   ├── manifest.json
│   └── README.md
├── model/
│   ├── model.json
│   ├── unknowns.jsonl
│   └── README.md
├── observations/
│   └── README.md
├── probes/
│   └── README.md
├── reconstructions/
│   └── README.md
├── scripts/
│   └── check.py
├── docs/
│   ├── PREWALK.md
│   └── superpowers/specs/
└── .gitignore
```

## Canonical state

Two files are canonical working state:

- `model/model.json`: current reconstructed semantic model
- `tasks/QUEUE.jsonl`: current local task state

Everything else constrains, sources, tests, or projects those files. A document may explain canonical state but may not silently override it.

Canonical files are single-writer surfaces. Parallel research workers do not edit them directly; a coordinator integrates completed task artifacts. This keeps the repository simple without requiring a database, lock service, or orchestration framework.

## Semantic substrate

The first-pass model uses a deliberately small vocabulary:

- THING: identifiable object or concept
- RELATION: typed connection between elements
- TRANSITION: operation that changes state or interpretation
- QUERY: read-only operation over state
- POLICY: authorization, visibility, or business-rule constraint
- EVENT: observable occurrence emitted by or consumed by the system

Do not add a new primitive while an existing one can represent the distinction without loss. Conversely, do not preserve a small vocabulary by forcing observably different behaviors into one primitive.

## Evidence states

Every reconstruction claim is classified as exactly one of:

- OFFICIAL: directly supported by Palantir public material
- OBSERVED: produced by an authorized black-box observation
- RECONSTRUCTED: implemented by an independent third-party reconstruction
- INFERRED: derived from supported facts
- UNKNOWN: unresolved

`RECONSTRUCTED` consensus does not become `OFFICIAL`. `UNKNOWN` must never be silently promoted to fact.

## Agent operating rules

`AGENTS.md` will require:

1. Search for an existing reconstruction before inventing one.
2. Public/observable behavior outranks guessed internals.
3. Separate official Palantir behavior, third-party reconstruction, and inference.
4. Never convert UNKNOWN into a fact.
5. Prefer the smallest explanatory model; expand only when a residual requires it.
6. Every model-changing task records the distinction that changed.
7. One task has one deliverable and one explicit completion condition.
8. No source dumping; extract only semantics that can change the model or a decision.
9. Implementation is a hypothesis test, not evidence about Palantir internals.
10. External writes or probes require explicit authorization for that target.
11. Never claim coverage without naming the scope denominator.
12. A primitive is accepted only if removing or merging it loses a REQUIRED observable distinction.
13. Workers never write `model/model.json` or `tasks/QUEUE.jsonl`; only the coordinator integrates canonical state.
14. A task is not DONE until its declared artifact exists and its `done_when` condition is checkable from repository state.

## Cold-start and coordination contract

A new agent must be able to recover the project without chat context.

Cold-start order:

1. read `AGENTS.md`
2. read `contracts/SCOPE.md`, `contracts/SEMANTICS.md`, and `contracts/ACCEPTANCE.md`
3. read `tasks/QUEUE.jsonl`
4. read only the source/model files named by the selected task
5. execute one task to its declared artifact and completion condition

Roles are intentionally minimal:

- COORDINATOR: owns writes to `tasks/QUEUE.jsonl` and `model/model.json`, assigns/claims work, validates task artifacts, integrates model changes, and runs `scripts/check.py`
- WORKER: reads canonical state, produces only the artifact named by its assigned task, and returns proposed distinctions/unknowns to the coordinator

If no coordinator is explicitly running, one agent may perform both roles serially. Parallel execution is allowed only when workers have disjoint artifact paths and no canonical writes.

A worker completion must return:

```json
{
  "task_id": "T001",
  "artifact": "reconstructions/example.md",
  "observed_distinctions": [],
  "proposed_model_changes": [],
  "new_unknowns": [],
  "done_when_result": "PASS"
}
```

This return object is a handoff contract, not a third canonical state store.

## Task state machine

```text
READY -> ACTIVE -> DONE
             \-> BLOCKED
             \-> UNKNOWN -> READY
```

`tasks/QUEUE.jsonl` contains exactly one current record per task ID. It is not an event log and is rewritten by the coordinator when task state changes.

A task record contains at minimum:

```json
{"id":"T001","state":"READY","depends_on":[],"artifact":"...","deliverable":"...","done_when":"...","scope_ids":[],"owner":null}
```

Rules:

- an ACTIVE task has a non-null owner
- a READY task may be claimed only when all dependencies are DONE
- two tasks intended for parallel execution must not share an artifact path
- DONE requires the artifact to exist and `done_when` to pass
- BLOCKED names an external dependency or authorization boundary
- UNKNOWN names the unresolved distinction and may return to READY only when a discriminator becomes available

The initial queue will cover:

- inventory known reconstructions
- inspect `gura105/operational-ontology`
- inspect `Przyval/openfoundry`
- inspect `syzygyhack/open-foundry`
- map official Palantir OSDK/API surface
- compute shared primitives
- record disagreements
- isolate Palantir-specific observable constraints
- compile `model/model.json` v0
- enumerate high-value unknowns
- generate discriminating probes
- synthesize the high-level architecture

Each task touching the model names the scope IDs it can change.

## Source strategy

Start with already-discovered high-value repositories rather than indiscriminate crawling:

- `palantir/osdk-ts`
- `palantir/foundry-platform-typescript`
- `palantir/ontology-starter-react-app`
- `palantir/workshop-iframe-custom-widget`
- `gura105/operational-ontology`
- `Przyval/openfoundry`
- `syzygyhack/open-foundry`

Each source entry records repository or locator, role, revision when pinned, license, and whether it is official or independent.

## Prewalk

Work outside-in:

1. Freeze the REQUIRED scope denominator.
2. Establish source inventory and provenance.
3. Coordinator assigns independent source-inspection tasks with disjoint artifact paths.
4. Workers extract public nouns/types, operations, failures, and transitions without editing canonical model state.
5. Coordinator compares independent reconstructions and checks proposed shared primitives against official Palantir public surfaces.
6. Compile the smallest model that explains the REQUIRED observable behavior.
7. Record disagreements as unknowns rather than averaging them away.
8. Probe only disagreements whose plausible outcomes could change the high-level model.
9. Recompute scope coverage.
10. Stop when remaining unknowns cannot change the core model under any currently plausible answer.

## Acceptance condition

`HIGH_LEVEL_READY` is true only when all are satisfied:

- every REQUIRED scope ID has status `COVERED`, `PARTIAL`, or `UNKNOWN`; none is silently absent
- every `COVERED` scope ID has at least one OFFICIAL or OBSERVED supporting behavior
- every major public operation inside a REQUIRED scope has a query/transition interpretation or is explicitly recorded as UNKNOWN
- every core primitive is necessary for at least one REQUIRED observable distinction
- independent reconstruction agreements are recorded but are not treated as proof of Palantir internals
- reconstruction disagreements are explicit
- Palantir-specific public constraints are separated from generic operational-ontology structure
- for every remaining UNKNOWN, plausible alternative answers have been checked for whether they would change the core model
- no remaining UNKNOWN can currently change the core primitive set or routing at the high-level target
- coverage is reported as `covered_required / total_required`, with PARTIAL and UNKNOWN listed separately
- every DONE task has its artifact and a checkable completion result
- `scripts/check.py` passes repository structural checks

A high coverage percentage alone is insufficient; one unresolved decision-changing scope item blocks `HIGH_LEVEL_READY`.

## Structural validator

`scripts/check.py` remains standard-library-only. It verifies:

- required files exist
- JSON/JSONL parse
- task IDs are unique
- task dependencies refer to existing tasks
- allowed task/evidence/scope states only
- task scope IDs refer to declared scope IDs
- task artifact paths are unique among concurrently runnable tasks
- ACTIVE tasks have owners
- DONE task artifacts exist
- `model/model.json` contains the required top-level keys
- source manifest entries contain required provenance fields
- every REQUIRED scope ID is represented in model coverage state

It does not attempt to prove that the reconstructed architecture is correct.

## Change policy

The repository starts minimal. New directories, schemas, databases, frameworks, or orchestration layers require a concrete failure of the current structure. The default repair is to extend an existing contract or record type, not introduce infrastructure.

A semantic primitive may be added, merged, or removed only with a named REQUIRED observable distinction demonstrating why the change is necessary.

## Completion boundaries

`BOOTSTRAP_COMPLETE` and `HIGH_LEVEL_READY` are distinct.

`BOOTSTRAP_COMPLETE` requires only that the agreed structure exists, contracts are populated, the initial task queue is valid, source seeds are recorded, `model/model.json` is syntactically valid, and the zero-dependency checker passes.

`HIGH_LEVEL_READY` requires the acceptance condition above. Repository scaffolding must never be reported as reconstruction completion.

## Counterfactual repair record

### Round 1 — hostile success

Counterfactual: the repository passes every original acceptance bullet while still producing a shallow taxonomy that misses a decision-changing public surface.

Failure mechanism: terms such as "major public concept" and "major public operation" had no denominator; completion could be achieved by narrowing attention after the fact. Consensus among third-party reconstructions could also be mistaken for evidence about Palantir.

Repair: freeze an explicit REQUIRED scope denominator, make coverage countable, require OFFICIAL/OBSERVED support for covered Palantir behavior, test whether unknowns can change the core model, and separate bootstrap completion from semantic completion.

### Round 2 — amnesia + parallel collision

Counterfactual: a capable agent receives only the repository, or several agents execute the queue concurrently. All follow the written rules yet either cannot determine how to proceed from a cold start or overwrite shared canonical files while producing individually valid work.

Failure mechanism: the original design named canonical files but did not define who may write them, how tasks are claimed, whether `QUEUE.jsonl` is state or an event log, what a worker must return, or how parallel work avoids write collisions.

Repair: define a five-step cold start, explicit COORDINATOR/WORKER roles, single-writer canonical state, one-current-record-per-task queue semantics, artifact ownership, dependency/claim rules, and a minimal worker handoff object. This preserves parallel source inspection without adding an orchestration service.
