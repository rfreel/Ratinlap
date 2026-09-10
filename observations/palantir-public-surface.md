# Palantir public surface map

Task: T005
Status: DONE
Evidence class: OFFICIAL

Pinned official sources inspected:

- `palantir/osdk-ts` @ `aec9d54682aef9497dbbc593ddec50d345567702`
- `palantir/foundry-platform-typescript` @ `d1fbe480fa7d22c13862d90946d06f8910871570`
- `palantir/ontology-starter-react-app` @ `7b31d4be74d4e584370afa795ae8520aaa2793db`
- `palantir/workshop-iframe-custom-widget` @ `de1ce669f01df4d11f05db8ec79e81daab129230`

This map records only public SDK/API/application-facing semantics. It makes no claim about Palantir's private storage, scheduling, indexing or service topology.

## S01 — ontology identity and type-instance split — COVERED

Official OSDK metadata has explicit definition categories with discriminants such as `type: "object"`, `type: "interface"`, `type: "action"`, and `type: "query"`. `ObjectTypeDefinition` carries an API name and compile-time metadata; object metadata contains an RID and primary-key metadata. The client uses an ontology RID when creating an ontology-bound client.

Witnesses:
- `packages/api/src/ontology/ObjectTypeDefinition.ts`
- `packages/api/src/ontology/ActionDefinition.ts`
- `packages/api/src/ontology/QueryDefinition.ts`
- `foundry-platform-typescript/README.md` client construction with ontology RID

Distinction retained: schema/definition identity is not the same object as a runtime object instance.

## S02 — objects and properties — COVERED

`ObjectMetadata` explicitly contains property metadata, `primaryKeyApiName`, `primaryKeyType`, link metadata, RID, display metadata, interface mappings and visibility metadata. Properties expose wire type, nullability/multiplicity and optional read-only/type-specific metadata.

Witness: `packages/api/src/ontology/ObjectTypeDefinition.ts`.

Distinction retained: object identity, property schema and property values are separate concepts.

## S03 — links and linked-object traversal — COVERED

Object metadata contains typed link definitions with target object type and multiplicity. ObjectSet documentation/examples expose link traversal through operations such as `pivotTo(...)`; the Workshop bridge also treats ObjectSets as typed by a concrete ObjectType when crossing the application boundary.

Witnesses:
- `packages/api/src/ontology/ObjectTypeDefinition.ts`
- OSDK ObjectSet/docs examples using `pivotTo`
- Workshop custom widget README ObjectSet variable semantics

Public evidence here establishes typed links/traversal. It does not establish a private graph-storage implementation.

## S04 — ObjectSet query/filter/aggregation semantics — COVERED

`MinimalObjectSet` composes fetch-page, async iteration, where/filter, link iteration and subscription interfaces. Official examples and unit-test support show set operations including union/intersect/subtract, `where(...)`, link `pivotTo(...)`, aggregation and page fetching. The observable client supports aggregation over pivoted, filtered or composed ObjectSets.

Witnesses:
- `packages/api/src/objectSet/ObjectSet.ts`
- `packages/client/src/objectSet/createObjectSet.ts`
- `packages/unit-testing/src/mock/createMockObjectSetWithResolver.ts`
- OSDK generated docs/examples for union, pivot and aggregation

Distinction retained: ObjectSet is a composable query expression/surface, not merely a materialized array.

## S05 — actions, validation, effects and visible failure states — COVERED

`ActionDefinition` is a distinct typed definition with API name, RID, parameters and metadata describing modified entities. Parameters include primitives, objects, interfaces, ObjectSets and structs. Client action application supports explicit `VALIDATE_ONLY` versus `VALIDATE_AND_EXECUTE`, optional returned edits, batch application, and raises `ActionValidationError` when validation is invalid.

Witnesses:
- `packages/api/src/ontology/ActionDefinition.ts`
- `packages/client/src/actions/applyAction.ts`
- `packages/api/src/actions/ActionReturnTypeForOptions.ts`

Official public evidence supports a semantic distinction among action definition, validation, execution and returned edits. It does not by itself prove that *all* Foundry state mutation paths internally use one action engine.

## S06 — functions and derived values — COVERED

The Platform SDK exposes Foundry functions execution packages/endpoints, including async execution/result retrieval and scopes such as `api:functions-execute`. OSDK ObjectSet APIs import `DerivedProperty`; official examples compute derived properties using composed ObjectSets and aggregations. `QueryDefinition` supports object, ObjectSet, struct, set/map and aggregation-shaped outputs.

Witnesses:
- `foundry-platform-typescript/packages/foundry.functions/...`
- `packages/api/src/objectSet/ObjectSet.ts`
- `packages/api/src/ontology/QueryDefinition.ts`
- generated OSDK derived-property examples

Distinction retained: callable computations/derived values are not identical to action mutations.

## S07 — authentication and authorization boundaries — COVERED

Official client setup uses OAuth providers and distinguishes public/client-facing from confidential/service-client flows. Platform functions expose required API scopes. Object metadata includes visibility/property security-related public metadata, while OSDK packages expose OAuth/auth construction separately from ontology definitions.

Witnesses:
- `foundry-platform-typescript/README.md`
- `ontology-starter-react-app/README.md`
- `foundry-platform-typescript/packages/foundry.functions/...`
- OSDK object/property security metadata surfaces

Distinction retained: authentication/authorization is an independent request boundary, not equivalent to domain action validation.

## S08 — asynchronous/loading/event behavior — COVERED

OSDK exposes Promise-based fetch/action/query behavior plus ObjectSet subscriptions and an observable client. Workshop's official custom-widget bridge explicitly represents loading, succeeded, reloading and failed values, permits the app to set those states, and exposes configured Workshop events that the app may execute.

Witnesses:
- `packages/api/src/objectSet/ObjectSet.ts`
- `packages/client/src/objectSet/createObjectSet.ts`
- OSDK documentation for `.subscribe(...)`
- `workshop-iframe-custom-widget/README.md`

Distinction retained: unavailable/loading/reloading/failure/success are observable states rather than a single nullable value.

## S09 — OSDK versus Platform API boundary — COVERED

The Platform TypeScript README explicitly distinguishes:

- ontology-specific OSDK clients bound to an ontology RID; and
- standalone Platform SDK clients that can call Foundry APIs across ontologies.

The Platform SDK repository provides namespace-specific Foundry/Gotham API bindings. The OSDK client itself invokes those lower-level packages, e.g. action application imports `@osdk/foundry.ontologies/Action`.

Witnesses:
- `palantir/foundry-platform-typescript/README.md`
- `palantir/osdk-ts/packages/client/src/actions/applyAction.ts`

Distinction retained: the ontology-programming surface and general platform API surface are related but not identical layers.

## S10 — application-facing interaction boundary — COVERED

The official React starter demonstrates a browser SPA obtaining an application-specific generated Ontology SDK and using object types through an authenticated client. The official Workshop iframe package exposes a bidirectional application boundary:

- Workshop -> custom app variable values;
- custom app -> Workshop variable state;
- custom app -> configured Workshop event execution.

ObjectSet values can cross this boundary by typed object-set representation/RID mechanisms.

Witnesses:
- `palantir/ontology-starter-react-app/README.md`
- `palantir/workshop-iframe-custom-widget/README.md`

Distinction retained: application/UI state consumes and manipulates exposed ontology/platform capabilities but is not itself the ontology's semantic definition.

## Official public-surface model after T005

The smallest structure directly supported by the inspected official code is:

```text
APPLICATION
    |
    v
OSDK / React / Workshop bridge
    |                       \
    | ontology-bound        \ general platform calls
    v                        v
ONTOLOGY DEFINITIONS       PLATFORM SDK
 object / interface          functions / admin / API namespaces
 action / query                  |
    |                            |
    +------------+---------------+
                 v
       public Foundry API boundary

ObjectSet = composable read/traversal/aggregation surface
Action    = typed validation/execution mutation surface
Query/function/derived value = computation/read surface
OAuth/scopes/security metadata = independent access boundary
Subscription/loading/event = temporal application boundary
```

## Things this inspection does NOT establish

- backing database/graph/index technology;
- private service decomposition;
- whether links are stored as rows/edges/documents internally;
- exact transaction boundaries of action effects;
- exact source-of-truth/write-back mechanism for every property;
- whether all product-level state mutation is action-gated internally;
- internal event bus implementation;
- consistency model across platform services.

These stay UNKNOWN unless separately observable.

## Licensing note

- `osdk-ts` public packages/source inspected here carry Apache-2.0 declarations/headers.
- `foundry-platform-typescript` generated/public packages carry Apache-2.0 declarations.
- `ontology-starter-react-app/package.json` declares `UNLICENSED`; use as official behavior/reference, not reusable implementation.
- `workshop-iframe-custom-widget` explicitly states Palantir License; use as official behavior/reference and do not treat public source as Apache/open-source code.
