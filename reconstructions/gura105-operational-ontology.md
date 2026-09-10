# gura105/operational-ontology inspection

Task: T002
Status: DONE
Source: https://github.com/gura105/operational-ontology
Pinned revision: `1a92960d67a890baa79cfd9043b83c3bc394eddb`
License: MIT
Independence group: `gura105-operational-ontology`

## Role

Minimal executable reference implementation of a Foundry-style operational ontology. The project explicitly separates the pattern from its own implementation choices and backs described behavior with executable tests.

## Implemented semantic core

- Schema side: object types, link types, action types, ownership/authority declarations, visibility predicates.
- Instance side: objects, links, applied actions, edit plans, audit records.
- Reads: `search`, `get`, `traverse`, `aggregate`, actor-scoped by visibility rules.
- Writes: only named actions through `Runtime.execute()`; no generic operational update API.
- Edits are data: `modify`, `create`, `link`, `unlink`; link instances and properties can change atomically through actions.
- Preconditions are business-rule checks and return machine-readable refusals.
- Every observed completed action attempt, including refusals, is recorded in an audit log.

## Authority model

The implementation distinguishes three state-authority classes:

1. source-backed — authoritative in an upstream system and changed through write-back;
2. ontology-owned — state whose system of record is the ontology store;
3. derived — computed state and never written.

`owned` marks ontology-owned object properties/types/links. `writeback:true` on an action declares that its edit plan changes source-backed state. The runtime rejects plans that cross or contradict the declared authority boundary.

Observed refusal codes include:

- `UNDECLARED_SOURCE_WRITE`
- `MISDECLARED_WRITEBACK`
- `MIXED_AUTHORITY`
- `SOURCE_CREATE_UNSUPPORTED`
- `NO_WRITEBACK_ADAPTER`
- `INVALID_EDITS`

## Action route / transition ordering

For this implementation:

1. validate parameters;
2. evaluate preconditions;
3. compute an edit plan without side effects;
4. dry-run that plan through the same commit path, then rollback;
5. check the plan against authority declarations;
6. write back to the source system when required;
7. commit local edits and audit entry transactionally.

The write-back adapter runs before local commit. Therefore source refusal leaves local state unchanged. The opposite failure remains possible: source write succeeds and local commit fails, creating divergence. This is explicitly declared and audited rather than hidden.

Failure records distinguish `WRITEBACK_FAILED`, `COMMIT_FAILED`, and `EXECUTION_CRASHED`. A process death between external write-back and local commit remains a stated uncovered window.

## Re-indexing semantics

- Loading is source replay, not a business decision.
- A fresh source snapshot replaces the base for loaded types.
- Ontology-owned edits are reapplied as an overlay.
- Source snapshots may not overwrite ontology-owned state.
- A re-index that would orphan ontology-owned edits is refused as a whole.
- Owned object/link state survives source refresh because the source is not authoritative for it.

## Security / policy boundary

Reads run as an actor and may be filtered by visibility predicates. A hidden object is intentionally indistinguishable from a nonexistent one to an ordinary scoped read. The action gate is an API/runtime contract, not a privilege boundary: in-process callers with direct database access could bypass it. The MCP server provides a process boundary with only generated model operations exposed.

## High-value distinctions proposed to the canonical model

- Type/schema and instance/state are distinct dimensions. `[S01]`
- Objects have stable identity and typed properties. `[S01,S02]`
- Links are typed state with traversal semantics, not merely presentation joins. `[S03]`
- Read/query operations and decision-changing writes are semantically distinct. `[S04,S05]`
- Named actions carry parameters, preconditions, edit plans and machine-readable failure states. `[S05]`
- Authorization/visibility and business preconditions are separate constraint classes. `[S05,S07]`
- State authority/ownership is independent of object identity. `[S02,S05]`
- External write-back is a side effect with observable failure-order semantics rather than an assumed distributed transaction. `[S05]`
- Audit/action history is instance data, not merely logging decoration. `[S05]`
- Source replay/re-indexing is distinct from a user decision/action. `[S05]`

## Do not generalize to Palantir without official support

The following are implementation choices, not evidence of Foundry internals: SQLite/storage choice, overlay implementation, write-back-before-commit ordering, fail-open visibility default, whole-plan single-authority restriction, specific refusal codes, and the exact seven-step executor.

## Source witnesses

- `README.md` at pinned revision — pattern, four properties, actor-scoped reads, generated MCP surface.
- `IMPLEMENTATION.md` at pinned revision — authority checks, failure ordering, transaction boundary, re-index behavior.
- `tests/core.test.ts` is identified by the implementation notes as the executable witness suite.
- `LICENSE` at pinned revision — MIT.
