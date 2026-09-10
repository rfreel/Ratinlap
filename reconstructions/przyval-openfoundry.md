# Przyval/openfoundry inspection

Task: T003
Status: DONE
Source: https://github.com/Przyval/openfoundry
Pinned revision: `67da90e6e28200e57079719699566a224f1805cb`
License: Apache-2.0
Independence group: `przyval-openfoundry`

## Role

A local-first Palantir Foundry emulator that intentionally exposes Foundry-shaped API routes. It is valuable as a compatibility hypothesis and executable behavioral corpus, not as evidence of Palantir's hidden implementation.

## Architecture

The pinned README describes a gateway plus separately named services for ontology, objects/ObjectSets, actions, authentication (`multipass`), datasets, admin, functions, monitoring (`sentinel`) and AIP, with a Vite application console. PostgreSQL can be used for persistence; otherwise services use local/in-memory persistence.

This decomposition is an implementation choice. The higher-value witness is the API and action behavior it attempts to emulate.

## Public/API-shaped surface

The gateway follows a `/api/v2` convention and exposes at least:

- ontologies and object types;
- object listing/get;
- `objectSets/loadObjects` and `objectSets/aggregate`;
- linked-object navigation;
- action type listing, action `apply`, action `validate`;
- datasets and branches;
- function execution;
- Compass-style resource navigation;
- AIP chat/agents;
- OAuth/token/current-user routes.

## ObjectSet/query behavior

The README declares:

- SearchJsonQueryV2 operators: `eq`, `gt`, `lt`, `gte`, `lte`, `isNull`, `contains`, `startsWith`, `and`, `or`, `not`, `prefix`, `anyTerm`;
- ObjectSet forms: base, filter, union, intersect, subtract, searchAround, staticSet;
- aggregate metrics: min, max, avg, sum, count, approximateDistinct;
- linked-object navigation through `searchAround` and link endpoints.

The repository contains a dedicated ObjectSet package and tests, making this a code-level rather than documentation-only reconstruction hypothesis.

## Action behavior inspected in source

`services/svc-actions/src/routes/v2/actions.ts` at the pinned revision exposes:

### apply

`POST /ontologies/:ontologyRid/actions/:actionApiName/apply`

- permission gate: `actions:execute`;
- unsupported ontology scoping is rejected;
- action is resolved by API name from a registry;
- parameters are validated before execution;
- invalid parameters return HTTP 400 with `INVALID_ARGUMENT`, `ValidationError`, and structured validation errors;
- an execution record is started before the optional handler is invoked;
- success is logged and returns `{rid,status:"SUCCEEDED",result?}`;
- thrown execution failure is logged and returns HTTP 500 `INTERNAL` / `ActionExecutionFailed`.

### validate

`POST /ontologies/:ontologyRid/actions/:actionApiName/validate`

- permission gate: `actions:read`;
- performs parameter validation without applying the action;
- returns `{valid, errors?}`.

### applyBatch

Batch action application processes requests individually. Validation or execution failures become per-item `FAILED` results; successful items become `SUCCEEDED`.

## Authentication / policy

The emulator advertises OAuth2 PKCE and client-credentials flows with JWT tokens. Route code demonstrates explicit per-operation permission checks such as `actions:execute` versus `actions:read`. This supports treating authentication and authorization as boundaries separate from the action's parameter validation.

## Application/runtime surface

The repository includes a Vite console plus Workshop-, Compass-, Pipeline-, AIP-, dataset- and function-like surfaces. These are useful coverage hints for the public product surface but not proof that service boundaries correspond to Palantir internals.

## High-value distinctions proposed to the canonical model

- Ontology/type metadata, object instances and actions are separately addressable API resources. `[S01,S02,S05]`
- ObjectSet is a composable read expression, not merely an array of fetched objects. `[S04]`
- filter/set algebra/traversal/aggregation are distinct query operators over ObjectSets. `[S03,S04]`
- action validation is separable from action application. `[S05]`
- action application has a durable/exposed execution identity and terminal status in this emulator. `[S05,S08]`
- permissions are checked independently of action parameter validation. `[S07]`
- functions are a separate callable surface from object-set reads and action writes. `[S06,S09]`
- application surfaces consume the gateway/API rather than defining ontology semantics themselves. `[S09,S10]`

## Material tensions to carry forward

- The emulator exposes object CRUD-shaped routes while the minimal operational-ontology reconstruction insists business decisions have no generic mutation path. This is a high-value disagreement for T007.
- Its action implementation logs and invokes handlers but does not, from the inspected route alone, establish the richer authority/write-back/audit semantics of `gura105/operational-ontology`.
- Service decomposition, PostgreSQL/in-memory choice and mocked AIP behavior must not be projected onto Palantir.

## Source witnesses

- `README.md` at pinned revision — architecture, features and API surface.
- `services/svc-actions/src/routes/v2/actions.ts` — apply/validate/applyBatch permission, validation, execution and failure behavior.
- `packages/object-set/` and tests — ObjectSet/aggregation implementation corpus.
- `LICENSE` — Apache License 2.0.
