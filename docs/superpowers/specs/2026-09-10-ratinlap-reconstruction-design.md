# Ratinlap reconstruction design

## Purpose

Ratinlap is a compact research-and-reconstruction workspace for understanding the public/observable architecture of Palantir Foundry-style operational ontology systems without pretending to know proprietary internals.

The repository should optimize for fast comprehension, explicit uncertainty, low operational overhead, and easy handoff between chat, coding agents, and human review.

## Scope

In scope:
- public Palantir SDK/API semantics
- independent open-source reconstructions
- objects, links, object sets, queries, actions, events, auth/policy boundaries
- high-level behavioral comparison
- small discriminating probes where public evidence disagrees
- a compact canonical model of the reconstructed architecture

Out of scope unless later promoted:
- proprietary source recovery
- claims about hidden storage/scheduling/runtime internals without evidence
- visual cloning of Palantir applications
- exhaustive compatibility engineering

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

Everything else explains, constrains, sources, tests, or projects those files.

## Semantic substrate

The first-pass model uses a deliberately small vocabulary:

- THING: identifiable object or concept
- RELATION: typed connection between elements
- TRANSITION: operation that changes state or interpretation
- QUERY: read-only operation over state
- POLICY: authorization/visibility/business-rule constraint
- EVENT: observable occurrence emitted by or consumed by the system

Do not add a new primitive while an existing one can represent the distinction without loss.

## Evidence states

Every reconstruction claim must be classifiable as one of:

- OFFICIAL: directly supported by Palantir public material
- OBSERVED: produced by an authorized black-box observation
- RECONSTRUCTED: implemented by an independent third-party reconstruction
- INFERRED: derived from other supported facts
- UNKNOWN: unresolved

`UNKNOWN` must never be silently promoted to fact.

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

## Task state machine

```text
READY -> ACTIVE -> DONE
             \-> BLOCKED
             \-> UNKNOWN -> READY
```

A task record contains at minimum:

```json
{"id":"T001","state":"READY","depends_on":[],"deliverable":"...","done_when":"..."}
```

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

## Source strategy

Start with already-discovered high-value repositories rather than broad GitHub crawling:

- `palantir/osdk-ts`
- `palantir/foundry-platform-typescript`
- `palantir/ontology-starter-react-app`
- `palantir/workshop-iframe-custom-widget`
- `gura105/operational-ontology`
- `Przyval/openfoundry`
- `syzygyhack/open-foundry`

Each source entry records repository, role, revision when pinned, license, and whether it is official or independent.

## Prewalk

Work outside-in:

1. Establish source inventory and provenance.
2. Extract public nouns/types.
3. Extract operations and transitions.
4. Compare independent reconstructions.
5. Intersect them with official Palantir public surfaces.
6. Compile the smallest model that explains the shared behavior.
7. Record disagreements as unknowns rather than averaging them away.
8. Probe only disagreements whose resolution could change the high-level model.
9. Stop when remaining unknowns are implementation detail rather than missing core primitives.

## Acceptance condition

`HIGH_LEVEL_READY` is true when all are satisfied:

- every major public concept has a role in the model
- every major public operation has a query/transition interpretation
- independent reconstruction agreements are explicit
- reconstruction disagreements are explicit
- Palantir-specific public constraints are separated from generic operational-ontology structure
- no unresolved unknown currently implies a missing core primitive
- `scripts/check.py` passes repository structural checks

## Structural validator

`scripts/check.py` should remain standard-library-only. It will verify:

- required files exist
- JSON/JSONL parse
- task IDs are unique
- task dependencies refer to existing tasks
- allowed task/evidence states only
- `model/model.json` contains the required top-level keys
- source manifest entries contain required provenance fields

It should not attempt to prove the reconstructed architecture is correct.

## Change policy

The repository starts minimal. New directories, schemas, databases, frameworks, or orchestration layers require a concrete failure of the current structure. The default repair is to extend an existing contract or record type, not introduce infrastructure.

## Completion boundary

This initial repository bootstrap is complete when the agreed structure exists, contracts are populated, the initial task queue is valid, source seeds are recorded, `model/model.json` is syntactically valid, and the zero-dependency checker passes.
