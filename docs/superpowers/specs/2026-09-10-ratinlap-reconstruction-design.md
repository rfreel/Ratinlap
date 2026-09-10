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

## Format and canonical state

The bootstrap deliberately uses only Markdown, JSON, JSONL, and Python standard library. No database, graph engine, task service, package manager, or framework is required to understand or validate the research state.

Two files are canonical working state:

- `model/model.json`: current reconstructed semantic model
- `tasks/QUEUE.jsonl`: current local task state

Everything else constrains, sources, tests, or projects those files. A document may explain canonical state but may not silently override it.

Canonical files are single-writer surfaces. Parallel research workers do not edit them directly; a coordinator integrates completed task artifacts. This keeps the repository simple without requiring a database, lock service, or orchestration framework.

## Semantic substrate

The initial candidate model uses a deliberately small vocabulary:

- THING: identifiable object or concept
- RELATION: typed connection between elements
- TRANSITION: operation that changes state or interpretation
- QUERY: read-only operation over state
- POLICY: authorization, visibility, or business-rule constraint
- EVENT: observable occurrence emitted by or consumed by the system

This vocabulary is a reconstruction hypothesis, not an authority claim. Do not add a new primitive while an existing one can represent the distinction without loss. Conversely, do not preserve a small vocabulary by forcing observably different behaviors into one primitive.

Before `HIGH_LEVEL_READY`, at least one materially different rival representation must be constructed from the same REQUIRED observations. If a rival expresses the same observable behavior with fewer distinctions, the candidate model must explain why its extra primitive is necessary or remove it.

## Evidence states

Every reconstruction claim is classified as exactly one of:

- OFFICIAL: directly supported by Palantir public material
- OBSERVED: produced by an authorized black-box observation
- RECONSTRUCTED: implemented by an independent third-party reconstruction
- INFERRED: derived from supported facts
- UNKNOWN: unresolved

`RECONSTRUCTED` consensus does not become `OFFICIAL`. `UNKNOWN` must never be silently promoted to fact.

Third-party source agreement is counted only across lineage-distinct independence groups. Multiple copies, forks, ports, agent-generated descendants, or implementations derived from the same upstream reconstruction count as one independence group unless a discriminating difference establishes otherwise.

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
15. Do not count two reconstructions as independent until source lineage has been checked.
16. Before closing a decision-changing UNKNOWN, construct the opposite plausible answer and verify whether it changes the model or routing.

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

- discover and lineage-deduplicate existing Foundry/operational-ontology reconstructions
- inspect `gura105/operational-ontology`
- inspect `Przyval/openfoundry`
- inspect `syzygyhack/open-foundry`
- map official Palantir OSDK/API surface
- compute shared observable distinctions
- record disagreements
- construct at least one rival representation of the same observations
- isolate Palantir-specific observable constraints
- compile `model/model.json` v0
- enumerate high-value unknowns
- run opposite-outcome tests on decision-changing unknowns
- generate discriminating probes where needed
- synthesize the high-level architecture

Each task touching the model names the scope IDs it can change.

## Source strategy

The named repositories are seeds, not the assumed complete corpus:

- `palantir/osdk-ts`
- `palantir/foundry-platform-typescript`
- `palantir/ontology-starter-react-app`
- `palantir/workshop-iframe-custom-widget`
- `gura105/operational-ontology`
- `Przyval/openfoundry`
- `syzygyhack/open-foundry`

Before deep inspection, perform a bounded prior-art discovery pass using materially different search families such as:

- Palantir Foundry emulator / clone / alternative
- operational ontology reference implementation
- Ontology SDK compatible implementation
- Foundry ObjectSet / action implementation

Stop discovery after two consecutive materially different search families yield no new architecture or REQUIRED behavioral distinction. This is a saturation heuristic, not proof that no other repository exists.

Each source entry records:

- repository or locator
- role
- revision when pinned
- license
- official versus third-party status
- `derived_from` when known
- `independence_group`
- notes on copied/forked/generated lineage where relevant

A reconstruction's popularity or agreement with another reconstruction does not increase confidence in Palantir behavior unless it contributes an independent observable distinction or points back to OFFICIAL/OBSERVED evidence.

## Prewalk

Work outside-in:

1. Freeze the REQUIRED scope denominator.
2. Run bounded prior-art discovery and lineage-deduplicate reconstruction sources.
3. Establish source inventory and provenance.
4. Coordinator assigns source-inspection tasks with disjoint artifact paths.
5. Workers extract public nouns/types, operations, failures, and transitions without editing canonical model state.
6. Coordinator compares lineage-distinct reconstructions and checks proposed shared distinctions against official Palantir public surfaces.
7. Compile the smallest candidate model that explains the REQUIRED observable behavior.
8. Construct a materially different rival representation from the same observations; ablate/merge candidate primitives and identify any lost observable distinction.
9. Record disagreements as unknowns rather than averaging them away.
10. For each decision-changing unknown, construct the opposite plausible answer and test whether model structure or routing changes.
11. Probe only disagreements whose plausible outcomes can change the high-level model.
12. Recompute scope coverage.
13. Stop when remaining unknowns cannot change the core model under any currently plausible answer.

## Acceptance condition

`HIGH_LEVEL_READY` is true only when all are satisfied:

- every REQUIRED scope ID has status `COVERED`, `PARTIAL`, or `UNKNOWN`; none is silently absent
- every `COVERED` scope ID has at least one OFFICIAL or OBSERVED supporting behavior
- every major public operation inside a REQUIRED scope has a query/transition interpretation or is explicitly recorded as UNKNOWN
- every core primitive is necessary for at least one REQUIRED observable distinction under ablation/merge testing
- at least one materially different rival representation has been fit to the same REQUIRED observations and its differences are recorded
- third-party reconstruction agreements are grouped by lineage and are not treated as proof of Palantir internals
- reconstruction disagreements are explicit
- Palantir-specific public constraints are separated from generic operational-ontology structure
- for every remaining decision-changing UNKNOWN, the opposite plausible answer has been tested for whether it changes the core model or routing
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
- source manifest entries contain required provenance and independence-group fields
- every REQUIRED scope ID is represented in model coverage state
- acceptance metadata records the rival-model and opposite-outcome checks before `HIGH_LEVEL_READY` may be true

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

### Round 3 — correlated consensus + self-confirming model

Counterfactual: every selected reconstruction agrees and `HIGH_LEVEL_READY` passes, but the agreement is caused by shared ancestry, copied code, common documentation, or the candidate model interpreting all evidence through its own primitives. A genuinely different representation would reveal that one "necessary" primitive is merely a modeling preference.

Failure mechanism: the design initially treated named repositories as if they were independent and treated the THING/RELATION/TRANSITION-family substrate as the frame used to judge its own sufficiency. This can create false confidence from correlated sources and a self-certifying ontology.

Repair: make named repositories seeds rather than the corpus, perform bounded prior-art discovery, record source lineage and independence groups, count consensus only across lineage-distinct sources, treat the semantic substrate as a candidate hypothesis, require a materially different rival representation, ablate/merge primitives, and invert every decision-changing UNKNOWN before closure.
