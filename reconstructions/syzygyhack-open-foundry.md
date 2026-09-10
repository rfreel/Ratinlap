# syzygyhack/open-foundry inspection

Task: T004
Status: DONE
Source: https://github.com/syzygyhack/open-foundry
Pinned revision: `1d7e1aa62208d32ed91d358f4503cf2d95523a7e` (0.3.0 release commit)
License: Apache-2.0
Independence group: `syzygyhack-open-foundry`

## Role

Independent, schema-driven ontology platform for operational digital twins. It is much broader than the minimal gura105 reference and provides a useful rival implementation for separating essential operational-ontology distinctions from architecture choices.

## Layered architecture

The technical specification defines:

1. Application Framework
2. Query & API Layer — GraphQL, REST, FHIR, SDKs
3. Action Framework — action types, execution, side effects
4. Security Layer + Sync Engine
5. Ontology Engine — schema registry, object store, relationship index
6. Storage Provider Interface

The spec requires adjacent-layer interfaces and prevents applications/API from bypassing the security/ontology stack. Storage is intentionally abstracted.

## Schema / ontology

Ontology Definition Language (ODL) extends GraphQL SDL with semantic directives. The schema is intended to drive API, permission and SDK generation.

Observed modeled categories include:

- ObjectTypes with exactly one primary identity field;
- interfaces/shared object shapes;
- first-class LinkTypes with their own IDs/properties and declared cardinality;
- link traversal fields with direction and optional historical traversal;
- ActionTypes for validated/auditable mutation;
- Functions as named read-only computations.

The spec distinguishes schema definitions from runtime instances and gives links independent identity when multiple historical relationships between the same endpoints must be distinguishable.

## Query / read behavior

The implementation/spec exposes GraphQL and REST query surfaces, filtering, aggregation, graph traversal, full-text search, temporal/history reads and subscriptions. The storage provider abstraction means these query semantics are intended not to depend on a specific backing engine.

## Action pipeline

The project describes every governed write as a named action and states a pipeline of roughly:

`validate -> authorize -> consent -> preconditions -> transactional execute -> side effects -> audit -> emit`

Action behavior is declared in manifests; effects operate on ontology state. The project also describes compensating transaction behavior when downstream side effects fail. This differs materially from gura105's write-back-before-local-commit choice and must remain a reconstruction disagreement rather than be averaged away.

## Function boundary

Functions are named computations with read-only ontology access. The technical spec explicitly states that functions cannot mutate state and that mutations go through Actions. It additionally specifies isolation/resource/network constraints for function execution. The sandbox mechanism is an implementation choice; the read/write semantic split is higher-value.

## Security / policy

The project uses OIDC authentication and OpenFGA relationship-based authorization, field-level redaction, consent and an append-only audit trail. The README warns that development mode can replace real enforcement with allow-all stubs; observations from such a mode therefore cannot establish production authorization semantics.

## Sync / authority

The Sync Engine covers JDBC connectors, Debezium CDC, mapping, overlay mode, conflict resolution and reconciliation. This supplies an independent witness that source integration and ontology state ownership are separate from the query/action model, while the specific CDC/storage choices remain implementation-specific.

## Storage

All persistence is behind a Storage Provider Interface. The project provides PostgreSQL+Apache AGE and in-memory implementations sharing conformance tests. This is direct counterevidence against treating a particular database technology as a necessary semantic primitive.

## High-value distinctions proposed to the canonical model

- Schema/type definitions are separate from runtime object/link/action instances. `[S01]`
- Objects and links have explicit identities/properties; links are first-class rather than implicit joins. `[S02,S03]`
- Query/read and action/write surfaces are distinct. `[S04,S05]`
- Functions are read-only computations; actions are the governed mutation mechanism. `[S05,S06]`
- Authorization/policy is a cross-cutting decision boundary independent of domain preconditions. `[S05,S07]`
- Events/subscriptions/history expose temporal behavior as an observable surface. `[S08]`
- Public API/SDK/application layers are separate from ontology/runtime/storage layers. `[S09,S10]`
- Storage engine and graph index technology can vary without changing the high-level ontology contract. `[S01-S05]`
- Sync/reconciliation is a boundary between ontology state and external systems, not equivalent to ordinary query or action semantics. `[S05,S09]`

## Material tensions to carry forward

- Side-effect/failure ordering differs from gura105.
- This design gives links independent IDs and history semantics more strongly than some other reconstructions.
- Security defaults differ by mode; no default should be generalized to Palantir.
- ODL/GraphQL SDL, OpenFGA, CEL, Postgres/AGE, Debezium, Kafka and domain packs are implementation choices, not Palantir evidence.

## Source witnesses

- `README.md` at pinned release — architecture, action pipeline, security/sync/storage behavior and maturity caveats.
- `docs/open-foundry-spec-v2.md` at pinned release — normative schema concepts, links, action types, functions and layered architecture.
- `LICENSE` — Apache License 2.0.
