# Executable semantic reference

This directory turns the accepted high-level public-surface reconstruction into a small executable model.

It is a **reference semantics artifact**, not a claim about Palantir's private implementation.

## What it preserves

- definition versus instance state;
- typed object identity and properties;
- typed relation state, traversal, and cardinality;
- immutable/composable ObjectSet expressions before materialization;
- READ, COMPUTE, VALIDATE, WRITE, OBSERVE, and application-interaction distinctions;
- access versus parameter versus domain-validation failure;
- validate-only versus executing action calls;
- optional returned edits and emitted observation events;
- explicit loading/succeeded/reloading/failed states;
- ontology-bound versus broader platform client facades;
- application value state plus configured event execution.

## Local implementation choices

These are deliberately **not** promoted to Palantir facts:

- in-memory dictionaries/lists are used for storage;
- equality is the only required `where()` predicate;
- count and numeric sum are the only required aggregations;
- actions stage object edits in a copied dictionary before commit;
- subscription events use a local `EventRecord` shape;
- access checks occur before parameter/domain checks in this reference;
- object loading and link loading are setup/infrastructure methods, not claims about Foundry user mutation routes.

## Non-claims

This runtime does not establish or emulate:

- private Foundry storage, indexing, service topology, queues, or transaction internals;
- universal action-only write closure;
- universal function purity;
- source-backed versus ontology-owned write-back behavior;
- exact Foundry error payloads or endpoint compatibility.

Those are separate compatibility questions.

## Run

```bash
python -m unittest runtime.test_reference -v
python scripts/run_reference.py
```

The runner writes `runtime/reference-report.json` and exits non-zero on any failing scenario or missing REQUIRED scope.
