# Executable model ablation

Phase 2 target: executable semantic core

Result: **MODEL_SURVIVES**

The runnable reference was implemented using the accepted four distinctions:

`DEFINITION / STATE / OPERATION / CONSTRAINT`

No fifth peer role was required.

## What execution forced us to make explicit

- `RELATION` remains a mandatory `STATE` subrole because traversal/cardinality cannot be represented as ordinary object properties without losing adjacency semantics.
- `OBJECT_SET` remains a state/expression subrole rather than a materialized array because composition precedes evaluation.
- `OPERATION` needs effect subroles including `READ`, `COMPUTE`, `VALIDATE`, `WRITE`, and `OBSERVE`; a mutation-only transition primitive would fail.
- `CONSTRAINT` must preserve at least access, parameter/schema, domain-validation, and cardinality distinctions. A single generic `invalid` state is insufficient.
- async application states are `STATE` values; they do not require a new top-level primitive.
- application event execution is an operation across an interface boundary; it does not require a top-level EVENT primitive.

## Ablations

### Merge DEFINITION into STATE

Fails S01/S05 because an object instance and an action/object type definition become indistinguishable except by recreating a definition tag. Distinction survives only if DEFINITION is reintroduced as a subrole.

### Merge OPERATION into STATE

Fails S04-S06/S08 because invocation/effect disappears. ObjectSet expressions, action definitions, and results can be stored, but the fact that something is invoked to read/compute/validate/write/observe must be recreated.

### Merge CONSTRAINT into OPERATION

Executable behavior still runs, but ACCESS, PARAMETER, DOMAIN, and CARDINALITY become ad-hoc branches inside operation code. The required distinction is no longer inspectable as model structure. This loses S05/S07 semantics.

### Remove relation subrole

Traversal can be encoded only by convention over arbitrary properties. Cardinality and typed adjacency cease to be first-class. S03 is lost.

### Materialize ObjectSet eagerly

Basic query results still work, but the public distinction between a composable ObjectSet and an object array disappears. S04 is lost.

## New implementation-level unknowns

Execution exposed useful compatibility questions but none changes the four-role model:

1. exact Foundry predicate/filter operator semantics;
2. exact ObjectSet evaluation/materialization behavior and error rules;
3. exact action error and returned-edit payloads;
4. exact subscription event payload/order/replay behavior;
5. exact authorization-versus-validation ordering;
6. exact link instance identity/history semantics.

These should become inputs to a future `/api/v2` compatibility-adapter phase, not new semantic primitives.

## Routing consequence

Proceed to a thin compatibility layer over this runtime. Do not build a second semantic engine inside the HTTP adapter.
