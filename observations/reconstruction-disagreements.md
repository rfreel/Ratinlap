# Reconstruction disagreements

Task: T007
Status: DONE

Disagreements are preserved because they identify implementation choices and remaining public-surface unknowns. `changes_high_level` means the answer could alter the reconstructed programming model or routing, not merely implementation technology.

## G01 — are all business mutations action-only?

Scopes: S02, S05, S09

Rival A — action-only operational write gate:
- gura105 exposes `Runtime.execute()` as the operational write path.
- syzygy describes governed writes through actions and current documentation says generic mutation is absent from the governed model.
- Aryan/Ontic emphasize important writes through governed actions.

Rival B — object CRUD coexists with action APIs:
- Przyval exposes object create/update/delete-shaped behavior in addition to action endpoints.

OFFICIAL:
- OSDK clearly exposes typed actions with validation/execution/edit semantics.
- The inspected official surface does not establish that every mutation available anywhere in Foundry must go through those actions.

changes_high_level: YES if the target claim is "all externally meaningful state changes are action instances"; NO if the model merely says "actions are a distinct mutation surface." Retain the weaker official statement and keep universal action-only closure UNKNOWN.

## G02 — state authority and write-back ownership

Scopes: S02, S05, S09

Rival A — explicit per-state authority:
- gura105 classifies state as source-backed, ontology-owned or derived and validates action plans against that authority line.

Rival B — synchronized platform state with connectors/overlays:
- syzygy models sync/CDC/overlay/reconciliation as a separate engine.

Rival C — local/emulated persistence:
- Przyval can store emulator state in PostgreSQL or local/in-memory persistence without reproducing an external source-of-record authority contract for every property.

OFFICIAL:
- public APIs establish objects/actions/platform integrations, but the inspected official source does not yet fix one universal property-ownership/write-back model.

changes_high_level: NO for core object/query/action primitives; YES for any stronger "operational ontology requires declared authority/write-back" invariant. Keep authority as a boundary/invariant candidate, not a Palantir fact.

## G03 — side-effect and commit ordering

Scopes: S05, S08

Rival A — gura105: validate/dry-run/authority check -> external write-back -> local commit/audit. External success followed by local commit failure can diverge.

Rival B — syzygy: transactional action pipeline with side effects/audit/emit plus compensating behavior on failures.

Rival C — Przyval: action route logs start -> invokes handler -> logs complete/failure; the inspected route does not encode gura105's authority/write-back semantics.

OFFICIAL:
- OSDK exposes validate/execute and returned edits but does not disclose a universal private commit order.

changes_high_level: NO. All rivals fit the same public `validate -> attempt -> success/failure/edit` abstraction. Exact ordering belongs below the current target unless a public API exposes it.

## G04 — link identity, cardinality and history

Scopes: S03

Rival A — gura105: typed link instances can be created/unlinked; cardinality is enforced but the minimal model need not imply rich independent link history IDs.

Rival B — syzygy: LinkTypes are strongly first-class; links have independent IDs, properties, active/historical state and explicit cardinalities.

Rival C — public OSDK: object metadata exposes typed target links/multiplicity and traversal, but inspected metadata does not require the same storage/history model.

changes_high_level: NO for `typed relation + traversal`; YES only if LINK INSTANCE must become a core entity with identity/history independent of its endpoints. Current evidence does not require that stronger primitive.

## G05 — security model and visibility defaults

Scopes: S07

Rival A — gura105 minimal runtime can default visibility open when no policy exists; hidden objects become indistinguishable from absent objects to ordinary reads.

Rival B — syzygy production posture is fail-closed with OIDC/OpenFGA/field policies, while its development mode deliberately uses allow-all stubs.

Rival C — Przyval uses explicit scopes/permission middleware; Ontic uses ABAC; Aryan uses role permissions.

OFFICIAL:
- OAuth/scopes/security metadata are clearly public boundaries. The inspected source does not justify a universal policy engine or default visibility behavior.

changes_high_level: NO. Retain `POLICY/access boundary`, not a specific policy calculus/default.

## G06 — functions/query semantics and mutation capability

Scopes: S04, S05, S06

Rival A — syzygy/Aryan/Ontic explicitly constrain functions to read-only computations and actions to mutation.

Rival B — official Platform SDK exposes functions execution and OSDK exposes QueryDefinition/derived properties, but inspected public TypeScript definitions do not by themselves prove every function implementation is incapable of side effects.

changes_high_level: YES only if we promote "function = pure/read-only" as an invariant. Do not. Retain `computation/query surface distinct from action API`; purity remains narrower UNKNOWN unless official behavior establishes it.

## G07 — async/event model

Scopes: S08, S10

Rival implementations use different mechanisms: WebSocket subscriptions, event buses, action execution histories, Workshop async values and app callbacks.

OFFICIAL:
- ObjectSet subscriptions and Workshop loading/succeeded/reloading/failed/event states are observable.

changes_high_level: NO. `observable temporal/asynchronous state` survives; transport and ordering semantics do not.

## G08 — physical storage and query execution

Scopes: S01, S02, S03, S04

Rivals:
- gura105: compact local store/overlay model;
- Przyval: PostgreSQL or local/in-memory persistence;
- syzygy: Storage Provider Interface with PostgreSQL+AGE and memory;
- Ontic: SQLite metadata + DuckDB data plane with ObjectSet SQL pushdown;
- Aryan: PostgreSQL/SQLAlchemy.

OFFICIAL:
- public OSDK/Platform contracts do not require any of these technologies.

changes_high_level: NO. This disagreement is affirmative evidence that database/query-engine technology should be omitted from the high-level semantic model.

## G09 — monolith/library versus microservices/layers

Scopes: S09, S10

Rivals range from an in-process runtime library to a gateway plus many services to a layered monorepo with replaceable interfaces.

OFFICIAL:
- public clients establish ontology-bound versus general platform API surfaces, not private deployment topology.

changes_high_level: NO. Keep API boundaries, discard service-topology guesses.

## G10 — audit/history as a core semantic object

Scopes: S05, S08

Rival A — gura105 makes applied/refused action attempts explicit audit instances; syzygy makes history/audit first-class platform behavior; Aryan records execution/audit evidence.

Rival B — Przyval exposes action execution logging/history but its semantics are narrower; official OSDK exposes returned edits/validation but the inspected definitions do not establish a universal append-only audit object for every attempt.

changes_high_level: NO for action semantics, YES if `AUDIT` were proposed as a seventh primitive. Current OFFICIAL support is insufficient to require that primitive. Treat audit/provenance as an observable relation/history capability when exposed, not a foundational primitive yet.

## G11 — schema language and generated surfaces

Scopes: S01, S09, S10

Rivals use plain TypeScript values, YAML, GraphQL-SDL-derived ODL, metadata stores, generated REST/GraphQL/SDKs or hand-built APIs.

OFFICIAL:
- generated Ontology SDKs and metadata definitions are public; no inspected evidence requires a particular schema source format for our reconstruction.

changes_high_level: NO. The necessary distinction is `schema definitions -> typed client/API surface`, not its source language.

# Routing result

Decision-changing unknowns retained for later inversion/probes:

1. whether universal action-only write closure is part of the Palantir public contract or merely a common operational-ontology design principle;
2. whether a declared source/ontology/derived authority distinction is required to explain any REQUIRED Palantir public behavior;
3. whether link instances require independent identity/history beyond typed traversal/multiplicity;
4. whether any callable function/query surface has public side-effect restrictions strong enough to alter the read/action boundary.

All other disagreements currently route below the high-level target as implementation choices.
