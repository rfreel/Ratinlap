# Palantir-specific observable constraints

Task: T009
Status: DONE

Only constraints supported by the inspected Palantir-owned public repositories are retained as Palantir-specific here. Third-party reconstruction behavior is excluded unless separately marked.

## P01 — ontology object definitions expose explicit identity/property/link metadata

Scopes: S01, S02, S03
Evidence: OFFICIAL

At pinned `palantir/osdk-ts` revision, `ObjectMetadata` exposes object type RID/API identity, `primaryKeyApiName`, `primaryKeyType`, properties, named links, target types, multiplicity, interface mappings and visibility metadata.

Implication: a reconstruction of the public programming model must distinguish definition metadata, runtime object identity, properties and links.

Not implied: physical storage/index layout.

## P02 — ObjectSet is a compositional client abstraction

Scopes: S03, S04
Evidence: OFFICIAL

The OSDK public types and implementation expose filtering (`where`), paging/iteration, link traversal, set composition (union/intersect/subtract), aggregation and subscription over ObjectSets. Official examples use `pivotTo(...)` and aggregate over composed sets.

Implication: modeling ObjectSet as only `Object[]` loses observable behavior.

Not implied: server-side query planner technology.

## P03 — action is a typed definition with separate application semantics

Scopes: S05
Evidence: OFFICIAL

`ActionDefinition`/`ActionMetadata` expose API identity, RID, typed parameters and modified-entity metadata. Parameter types include primitives, objects, interfaces, ObjectSets and structs.

Implication: an action definition is not identical to an arbitrary endpoint or direct state patch.

## P04 — validation-only and validation+execution are distinct public action modes

Scopes: S05
Evidence: OFFICIAL

OSDK `applyAction` sends `VALIDATE_ONLY` when `$validateOnly` is set and otherwise sends `VALIDATE_AND_EXECUTE`. Invalid validation is surfaced as `ActionValidationError`. Optional returned edits are a separate result mode; batch actions are separately supported.

Implication: VALIDATION and EXECUTION must remain distinguishable transitions/operation modes.

Not implied: exact internal transaction ordering or universal action-only mutation closure.

## P05 — query definitions have typed parameters and typed structured outputs

Scopes: S04, S06
Evidence: OFFICIAL

`QueryDefinition`/`QueryMetadata` expose API identity, version, parameters and outputs spanning primitives, objects, interfaces, ObjectSets, sets, arrays, unions, structs, maps and aggregation shapes.

Implication: callable query/computation behavior deserves an explicit operation role even when it does not mutate ontology state.

## P06 — derived-property/object-set computation is public behavior

Scopes: S04, S06
Evidence: OFFICIAL

OSDK ObjectSet code imports derived-property definitions; official examples derive properties by traversing/pivoting ObjectSets and aggregating linked values.

Implication: a value may be computed from ontology relationships/query semantics rather than stored as a direct property.

Not implied: persistence/materialization strategy for derived values.

## P07 — general Platform SDK and ontology-bound OSDK are distinct clients/surfaces

Scopes: S09
Evidence: OFFICIAL

`foundry-platform-typescript` documents a standalone `createPlatformClient(stack, auth)` not tied to one ontology, while ontology OSDK `createClient(stack, ontologyRid, auth)` is bound to an ontology RID. Platform packages expose Foundry/Gotham API namespaces and are also usable alongside OSDK.

Implication: the high-level model needs an ontology semantic surface nested within or adjacent to a broader platform API boundary.

## P08 — authentication is explicit and client mode matters

Scopes: S07, S10
Evidence: OFFICIAL

Official examples construct OAuth providers. The starter application distinguishes browser/client-facing public clients from confidential clients and requires configured redirect/CORS/application credentials. Platform functions also declare execution scopes in generated API bindings.

Implication: identity/authorization context is not implicit application state.

## P09 — subscriptions and asynchronous state are public application semantics

Scopes: S08
Evidence: OFFICIAL

OSDK ObjectSets expose subscription behavior. Workshop's custom-widget bridge represents loading, succeeded, reloading and failed states, and allows an application to set loading/reloading/success/failure on bridged values.

Implication: `missing`, `loading`, `reloading`, `failed` and `ready` cannot be indiscriminately collapsed into `null` without losing public behavior.

## P10 — Workshop/custom applications communicate through an explicit bidirectional contract

Scopes: S08, S10
Evidence: OFFICIAL

The official Workshop iframe package supports Workshop -> app variable values, app -> Workshop variable-state updates, and app -> Workshop configured-event execution. ObjectSet values have explicit cross-boundary representation constraints and temporary ObjectSet RID support in newer clients.

Implication: application integration is a typed interaction boundary, not a direct read/write of hidden Workshop internals.

## P11 — public API packages expose asynchronous function execution as a separate platform capability

Scopes: S06, S09
Evidence: OFFICIAL

`foundry-platform-typescript` includes Foundry functions bindings, including async query execution/result retrieval/cancel surfaces and an `api:functions-execute` scope.

Implication: computation/execution exists as a broader platform capability distinct from ontology ObjectSet reads and ontology actions.

Not implied: purity of every function implementation.

# Explicit UNKNOWN constraints

These are intentionally not promoted:

| Claim | Evidence state | Scopes | Why UNKNOWN |
|---|---|---|---|
| Every externally meaningful Foundry write is action-gated | UNKNOWN | S05,S09 | Actions are official; universal closure was not established by inspected public code. |
| Every property has an exposed source-backed/ontology-owned/derived authority class | UNKNOWN | S02,S05 | Strong in gura105, not established as universal official contract. |
| Link instances necessarily have independent persistent IDs/history | UNKNOWN | S03 | Official OSDK proves typed links/traversal/multiplicity, not this stronger representation. |
| All ontology functions/queries are guaranteed side-effect-free | UNKNOWN | S05,S06 | Public surfaces distinguish them from actions; universal side-effect restriction was not established from inspected TypeScript contracts. |
| Action external side effects use one fixed commit order | UNKNOWN | S05,S08 | Reconstructions disagree; public OSDK does not expose private commit ordering. |
| Palantir uses any specific graph/database/event-bus technology | UNKNOWN | S01-S09 | Public client contracts do not require it. |
| Public SDK package boundaries equal Palantir internal service boundaries | UNKNOWN | S09 | API organization is observable; deployment topology is not. |

# Retained Palantir public contract

```text
Ontology-bound semantic definitions
  object / interface / action / query
             |
             +--> typed objects/properties/links
             +--> composable ObjectSets / traversal / aggregation / subscription
             +--> typed action validation + execution + optional edits
             +--> typed query/computation outputs

Authentication / authorization context constrains calls.

Ontology OSDK != general Platform SDK.

Application boundary:
  generated OSDK / React
  Workshop variables + async states + configured events
```

This is the Palantir-specific layer the canonical model is allowed to rely on without importing third-party implementation assumptions.
