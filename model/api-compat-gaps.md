# API compatibility residuals after first `/v2` slice

Status: first thin adapter implemented over `runtime/reference.py`; no second semantic engine.

## What the slice establishes

- official public route shapes can be mapped onto the four-role semantic runtime;
- the tagged ObjectSet wire grammar maps directly to existing compositional ObjectSet expressions;
- action `VALIDATE_ONLY` versus `VALIDATE_AND_EXECUTE` maps without changing runtime semantics;
- a semantic invalid action can remain HTTP 200 with `validation.result=INVALID`;
- OSDK-recognizable object identity can be emitted as `__apiName` + `__primaryKey`.

## Residuals, ordered by likelihood of blocking a real TypeScript OSDK smoke test

1. **Exact generated ontology metadata/provider contract.** A real OSDK client needs generated object/action definitions and ontology metadata beyond the simple object-type response in this slice. This is the next blocking boundary.
2. **Exact wire object metadata.** Determine when `__rid`, title metadata, null omission, selected properties, property-security metadata, and other fields are required by the OSDK path being tested.
3. **Exact SearchJsonQueryV2 grammar.** Equality works; OSDK `where()` can generate additional tagged operators and nested boolean queries. Aggregate request/response now uses the official array/grouped envelope, but non-empty `groupBy` and metrics beyond count/sum remain deferred.
4. **Exact ObjectSet serialization.** Support the variants actually emitted by a minimal OSDK program, not the entire public union preemptively.
5. **Action parameter DataValue conversion.** Primitive string/int parameters work because the local demo uses scalar values; object, ObjectSet, attachment, marking, structs, and other parameter types need official wire conversion.
6. **Action validation detail.** Current response preserves `VALID|INVALID` but does not synthesize full `submissionCriteria` and per-parameter evaluated constraints.
7. **Action edit receipts.** Current modify-object receipt follows the public `ActionResults -> edits` family but only emits the fields needed by the observed OSDK remapper path; add link/create/delete/large-scale variants only when a smoke test requires them.
8. **Pagination.** Current adapter rejects page tokens. Real OSDK `fetchPage` may require them even for larger local fixtures.
9. **Authentication.** Replace `X-Ratinlap-Actor` with a separate auth adapter only when an OSDK transport smoke test reaches that boundary. Do not entangle auth with ontology semantics.
10. **Consistency/storage semantics.** Eventual versus immediate visibility, storage-v1/v2 limits, snapshots, branches, scenarios, and transactions remain outside this reference slice.

## Next routing decision

Do **not** widen endpoint count next.

The smallest high-value next test is:

```text
minimal generated TypeScript OSDK definition
        -> @osdk/client transport
        -> Ratinlap /v2 adapter
        -> fetch one object / filtered ObjectSet
        -> optionally validate one action
```

First inspect exactly which metadata-provider and wire fields that smoke path consumes. Add only those missing contracts. If the real OSDK can fetch/filter against this server after that, the compatibility strategy is validated; if not, the failure trace selects the next field/variant.
