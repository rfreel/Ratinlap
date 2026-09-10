# High-value unknowns

Task: T011
Status: DONE

Starting set comes from T007. An unknown is decision-changing only if two currently plausible answers require a different core primitive, operation-effect class, or mandatory routing rule at the S01-S10 high-level target.

## U-A — universal action-only write closure

Scopes: S05, S09
Question: Does every externally meaningful Foundry business mutation necessarily route through an Action, or do other mutation surfaces coexist?

Current evidence:
- OFFICIAL: typed actions support validation/execution/returned edits.
- RECONSTRUCTED: gura105/syzygy favor action-only governed writes; Przyval exposes CRUD-shaped object behavior too.

Discriminator if needed: enumerate official mutation operations outside the action namespace and determine whether they are administrative/schema/data-plane operations versus business-object state changes.

Initial decision-changing: YES for an `ALL_WRITES -> ACTION` invariant, but not for the four-role primitive basis.

Robust routing: model `OPERATION.effect=WRITE`; `action` is one official WRITE operation family. Do not assert universal closure.

After robust routing: NO core-model change is forced by either answer.

## U-B — explicit state authority/write-back taxonomy

Scopes: S02, S05, S09
Question: Must public Palantir semantics classify state as source-backed, ontology-owned, derived (or equivalent), with observable write-back routing?

Current evidence:
- RECONSTRUCTED: gura105 makes this explicit; syzygy models sync/overlay/reconciliation; emulators differ.
- OFFICIAL inspected surface: insufficient for a universal taxonomy.

Discriminator if needed: inspect official property/action/writeback APIs for exposed authority metadata and failure behavior.

Initial decision-changing: YES for a mandatory `AUTHORITY` invariant and external-side-effect router; NO for primitive basis.

Robust routing: authority, when exposed, is `CONSTRAINT`/definition metadata on a WRITE operation. Absence of a universal authority taxonomy does not alter DEFINITION/STATE/OPERATION/CONSTRAINT.

After robust routing: NO core-model change is forced.

## U-C — independent identity/history for link instances

Scopes: S03
Question: Are link instances always independently identifiable/historical entities, or can public semantics be satisfied by typed adjacency with target/multiplicity?

Current evidence:
- OFFICIAL: typed links, target type, multiplicity, traversal are established.
- RECONSTRUCTED: syzygy strongly reifies link IDs/history; other implementations vary.

Discriminator if needed: inspect official link APIs/metadata for link-instance RIDs, link properties and history operations.

Initial decision-changing: YES only if the canonical relation state schema required a persistent independent identity for every link.

Robust routing: `STATE.kind=RELATION` requires typed endpoints/traversal but leaves optional identity/history fields capability-dependent.

After robust routing: NO core-model change is forced.

## U-D — purity/side effects of function/query surfaces

Scopes: S05, S06, S09
Question: Are all public query/function operations guaranteed side-effect-free relative to ontology/business state?

Current evidence:
- OFFICIAL: query/function surfaces are distinct from Action; function execution APIs exist.
- RECONSTRUCTED: several projects explicitly make functions read-only.
- Inspected OFFICIAL TypeScript definitions do not establish universal purity.

Discriminator if needed: inspect official function/query documentation/contracts for mutation restrictions and side-effect declarations.

Initial decision-changing: YES if `function => COMPUTE-only` were mandatory.

Robust routing: operation effect is a property of the exposed operation contract, not inferred from its noun. Known ObjectSet/query operations are READ/COMPUTE; unknown function side effects remain unspecified. No universal purity invariant is required.

After robust routing: NO core-model change is forced.

# Non-decision-changing implementation unknowns

These do not alter current high-level routing under either plausible answer:

- database/graph/index technology;
- service topology;
- exact transaction isolation/commit ordering;
- event-bus transport and ordering;
- cache/materialization strategy;
- authorization engine implementation;
- audit storage format;
- schema source language;
- search planner and ObjectSet pushdown implementation.

# Result

No remaining known unknown requires a new core primitive. The four initially decision-changing questions can be quarantined behind conservative capability/constraint fields so either plausible answer fits the same routing:

```text
DEFINITION
   |
   v
OPERATION(effect, capabilities)
   |
   +-- constrained by CONSTRAINT
   |
   +-- consumes/produces STATE
```

T012 must still explicitly invert each question and verify both outcomes against routing before `opposite_outcome_checks_complete` can become true.
