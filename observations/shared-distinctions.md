# Shared observable distinctions

Task: T006
Status: DONE

This file intersects the official Palantir public surface with lineage-distinct reconstructions. Agreement among reconstructions is recorded separately from OFFICIAL support; common implementation choices do not become Palantir facts.

## D01 — definition/type identity is distinct from instance identity

Scopes: S01, S02

OFFICIAL: OSDK exposes `ObjectTypeDefinition`, object metadata, primary-key metadata, RIDs, action definitions and query definitions as schema/definition objects distinct from runtime object values.

RECONSTRUCTIONS: gura105 explicitly separates type definitions from object/link/action instances; syzygy ODL separates ObjectType/LinkType/ActionType from instances; Przyval exposes ontology type metadata separately from object resources; Ontic and Aryan do the same.

Retain: yes.

Do not infer: private schema-registry implementation.

## D02 — an object has typed properties plus stable identifying semantics

Scopes: S01, S02

OFFICIAL: `ObjectMetadata` contains property metadata, primary-key API name/type and RID; property schema records type/nullability/multiplicity and other metadata.

RECONSTRUCTIONS: all primary executable reconstructions model typed objects with identifiers/keys and property values.

Retain: yes.

Do not infer: physical key/index representation.

## D03 — links are typed relationships that support traversal

Scopes: S03

OFFICIAL: OSDK object metadata includes named links with target types/multiplicity; public ObjectSet examples expose traversal such as `pivotTo(...)`.

RECONSTRUCTIONS: gura105 models typed link instances and traversal; syzygy models first-class link types/instances; Przyval exposes linked-object endpoints and `searchAround`; Ontic/Aryan expose relationship traversal.

Retain: yes.

Do not infer: graph database, edge table, link-RID policy or history representation.

## D04 — ObjectSet/query semantics are compositional, not equivalent to a materialized list

Scopes: S04

OFFICIAL: `MinimalObjectSet` composes filtering, fetch-page, async iteration, link iteration and subscription; official implementation/examples support union/intersect/subtract, `where`, traversal/pivot and aggregation over composed ObjectSets.

RECONSTRUCTIONS: Przyval implements base/filter/union/intersect/subtract/searchAround/staticSet; Ontic compiles ObjectSet expressions to SQL; other reconstructions expose filtered/traversed/aggregated object collections.

Retain: yes.

Do not infer: query planner, SQL pushdown, cache/index strategy.

## D05 — action definition, validation and execution are separate observable concepts

Scopes: S05

OFFICIAL: `ActionDefinition` carries typed parameters and modified-entity metadata. OSDK action application distinguishes `VALIDATE_ONLY` from `VALIDATE_AND_EXECUTE`, can return edits, and exposes invalid validation as a structured action error.

RECONSTRUCTIONS: gura105 named actions validate/precondition before effects; Przyval has separate apply and validate endpoints with separate permissions; syzygy defines action schemas/manifests and an action pipeline; Ontic/Aryan expose governed action execution.

Retain: yes.

Do not infer: one universal private executor or exact transaction order.

## D06 — read/computation operations are semantically distinguishable from mutation actions

Scopes: S04, S05, S06

OFFICIAL: ObjectSet/query APIs are read/computation surfaces; action application is a separate typed API. Platform SDK exposes functions execution separately from ontology actions; OSDK exposes derived-property/query definitions.

RECONSTRUCTIONS: gura105 separates reads from named write actions; syzygy declares functions read-only and actions mutating; Ontic/Aryan distinguish read-only functions/query paths from governed actions.

Retain: yes at the public programming-model level.

Caveat: official public evidence inspected does not prove that every internal platform mutation is action-gated.

## D07 — authorization is an independent boundary from domain/action validation

Scopes: S05, S07

OFFICIAL: OAuth client construction and API scopes are separate from ontology/action parameter validation. Public metadata exposes visibility/property-security concepts.

RECONSTRUCTIONS: Przyval checks `actions:execute` or `actions:read` separately from parameter validation; gura105 separates actor visibility from business preconditions; syzygy has an explicit authorization/security layer; Ontic/Aryan expose ABAC/RBAC separately from business action validation.

Retain: yes.

Do not infer: a particular policy engine such as OpenFGA, ABAC or ReBAC.

## D08 — asynchronous and temporal state is part of the application contract

Scopes: S08, S10

OFFICIAL: OSDK operations are asynchronous and ObjectSets expose subscriptions. Workshop bridge values explicitly distinguish loading, succeeded, reloading and failed states, and expose event execution.

RECONSTRUCTIONS: event/execution histories and asynchronous operations appear in the larger reconstructions, although mechanisms differ.

Retain: yes as an observable application/runtime distinction.

Do not infer: event-bus technology or internal message ordering.

## D09 — ontology-bound SDK and general platform API are distinct public layers

Scopes: S09

OFFICIAL: `createClient` is ontology-RID-bound while `createPlatformClient` is not tied to a specific ontology; Platform SDK exposes Foundry/Gotham namespaces. OSDK uses lower-level Foundry platform packages for actions.

RECONSTRUCTIONS: emulator/independent projects likewise separate semantic/ontology APIs from broader platform services, though their exact boundaries vary.

Retain: yes.

## D10 — application interaction is downstream of exposed semantic/platform contracts

Scopes: S10

OFFICIAL: official React starter consumes a generated Ontology SDK; Workshop custom widgets exchange typed values/events with Workshop through an explicit bridge.

RECONSTRUCTIONS: UI/app layers sit above semantic/API layers in Przyval, syzygy, Ontic and Aryan.

Retain: yes.

Do not infer: a specific Palantir frontend architecture.

# Common reconstruction claims NOT promoted by this intersection

The following recur in one or more reconstructions but lack enough inspected OFFICIAL support to call them Palantir invariants:

- every business write in the whole platform is action-gated;
- explicit source-backed vs ontology-owned vs derived authority is represented exactly as gura105 models it;
- an append-only audit instance is created for every attempted action;
- write-back occurs before or after local commit in one universal order;
- links necessarily have independent stored IDs/history;
- PostgreSQL, AGE, DuckDB, SQLite, Kafka, Debezium, OpenFGA or any specific storage/policy technology is architecturally necessary;
- a particular microservice split is Palantir's internal split;
- a specific visibility default (fail-open/fail-closed) applies generally.

# Intersection result

The public-surface core that survives lineage and implementation changes is:

```text
DEFINITIONS/TYPES
    object/interface/action/query definitions
             |
             v
STATE/INSTANCES
    typed objects + properties + typed links
             |
       +-----+----------------------+
       |                            |
       v                            v
COMPOSABLE READS               NAMED ACTIONS
ObjectSet/query/traversal       validate / execute / edits
aggregation/functions                |
       |                             v
       +----------------------> changed exposed state

AUTHORIZATION constrains requests independently of domain validation.
ASYNC/SUBSCRIPTION/EVENT states expose change over time.
APPLICATIONS consume the ontology SDK and/or broader platform API.
```

This intersection is descriptive of the inspected public programming model. It intentionally leaves physical implementation below the public boundary unknown.
