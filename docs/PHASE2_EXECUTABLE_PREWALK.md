# Phase 2 prewalk — executable reconstruction core

## Target

Turn the accepted high-level public-surface model into the smallest runnable semantic reference that can falsify the model before any HTTP/API clone work begins.

This phase does **not** claim Palantir internal equivalence. It implements only distinctions already established in `docs/HIGH_LEVEL_MODEL.md` and marks implementation choices as local reference behavior.

## Why this comes next

`HIGH_LEVEL_READY` established four roles — `DEFINITION / STATE / OPERATION / CONSTRAINT` — and public distinctions for typed objects/links, composable ObjectSets, action validate-vs-execute, access constraints, async states, subscriptions, and the ontology-bound versus platform-client boundary.

The next useful test is executable: if these distinctions cannot compose cleanly in a small runtime, the model is incomplete.

## Structure

```text
runtime/
  reference.py          stdlib-only in-memory semantic runtime
  scenarios.py          executable representative scenarios
  test_reference.py     unit/conformance tests
  README.md             exact claims and non-claims
scripts/
  run_reference.py      one-command scenario runner
```

No framework, database, web server, package manager, generated SDK, or copied third-party runtime is introduced.

## Runtime contract

The runtime must preserve these distinctions explicitly:

1. definition versus instance state;
2. object identity versus properties;
3. typed relation state versus arbitrary properties;
4. ObjectSet expression versus materialized object list;
5. READ / COMPUTE / VALIDATE / WRITE / OBSERVE effects;
6. access denial versus schema/parameter invalidity versus domain validation failure;
7. validate-only action invocation versus state-changing action execution;
8. action edits versus emitted observation events;
9. loading / succeeded / reloading / failed async states;
10. ontology-bound client versus broader platform client.

## Deliberate limits

- only equality predicates are required in the first `where()` operator;
- only count and numeric sum aggregations are required;
- link cardinality support is `ONE_TO_ONE`, `ONE_TO_MANY`, `MANY_TO_ONE`, `MANY_TO_MANY`;
- no claim is made about Palantir transaction ordering, storage, indexing, event transport, universal function purity, or universal action-only write closure;
- subscription payload shape is local reference behavior and must be documented as such.

## Tasks

- T015: implement and test the semantic reference runtime.
- T016: add representative scenarios spanning S01-S10.
- T017: add a one-command runner and machine-readable scenario report.
- T018: run ablation/failure review and record whether executable behavior exposes a missing primitive or routing rule.

## Acceptance

`EXECUTABLE_CORE_READY` when:

- `python -m unittest runtime.test_reference -v` passes;
- `python scripts/run_reference.py` exits 0 and reports every scenario PASS;
- each S01-S10 appears in at least one executable scenario;
- at least one negative scenario distinguishes ACCESS, PARAMETER, and DOMAIN validation failures;
- validate-only is proven non-mutating;
- ObjectSet is proven compositional before materialization;
- relation traversal and cardinality are exercised;
- subscription/async/client-boundary distinctions are exercised;
- the ablation review states either `MODEL_SURVIVES` or names the model repair required.

## Stop condition

Do not add an HTTP server or attempt endpoint compatibility in this phase. If the semantic core survives, the next phase can be a thin `/api/v2` compatibility adapter rather than a second semantic implementation.
