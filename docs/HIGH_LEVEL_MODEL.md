# High-level Palantir public-surface reconstruction

Task: T014
Status: DONE

## Acceptance summary

Target denominator: S01-S10 from `contracts/SCOPE.md`.

```text
COVERED REQUIRED: 10 / 10
PARTIAL:            0
UNKNOWN SCOPE:      0
```

Every REQUIRED scope has at least one OFFICIAL witness in `observations/palantir-public-surface.md`. This is high-level public-programming-model coverage, not exhaustive endpoint or product compatibility.

`HIGH_LEVEL_READY = true` for this denominator.

Remaining unknowns in `model/unknowns.jsonl` are compatibility/implementation questions whose opposite plausible outcomes were tested and do not change the core semantic roles or current conservative routing.

# One-screen model

```text
                         APPLICATIONS
                 React / custom app / Workshop
                             |
                  typed values, events, async state
                             |
             +---------------+----------------+
             |                                |
             v                                v
      ONTOLOGY-BOUND OSDK               PLATFORM SDK
         bound to ontology RID        broader Foundry/Gotham APIs
             |                                |
             +---------------+----------------+
                             |
                             v
                   PUBLIC FOUNDRY BOUNDARY

     +----------------------------------------------------+
     | DEFINITION                                         |
     | ontology context                                   |
     | object type / interface / property / link metadata |
     | action definition / query definition               |
     +-----------------------------+----------------------+
                                   |
                          defines/constrains
                                   v
     +----------------------------------------------------+
     | STATE                                              |
     | object + property values                           |
     | typed relation/link                                |
     | ObjectSet/query expression/result                  |
     | derived result                                     |
     | async/loading/event occurrence                     |
     +-----------------------------+----------------------+
                                   ^
                                   |
                           consumes / produces
                                   |
     +-----------------------------+----------------------+
     | OPERATION                                          |
     | READ     where / fetch / traverse / set algebra    |
     | COMPUTE  aggregate / query / function              |
     | VALIDATE action validation                         |
     | WRITE    action apply / batch apply                |
     | OBSERVE  subscribe                                 |
     | APP      Workshop value/event interaction          |
     +-----------------------------+----------------------+
                                   |
                           permitted/limited by
                                   v
     +----------------------------------------------------+
     | CONSTRAINT                                         |
     | schema/type constraints                            |
     | action/domain validation                           |
     | OAuth/scopes/access                                |
     | link multiplicity/cardinality metadata             |
     | capability-specific constraints                    |
     +----------------------------------------------------+

PRIVATE STORAGE / INDEX / SERVICE TOPOLOGY / EVENT BUS = OUTSIDE MODEL
```

# The four roles

## 1. DEFINITION

A DEFINITION describes allowable shape or callable capability rather than being the current business value itself.

Official public examples include:

- ontology identity/context;
- object types and interfaces;
- property metadata and primary-key metadata;
- link metadata;
- action definitions with typed parameters and modified-entity metadata;
- query definitions with typed parameters and outputs.

The key distinction is schema/definition versus instance/runtime state, not any particular schema language or registry implementation.

## 2. STATE

STATE is an identifiable/current/historical/query/application value that operations consume or produce.

Important state kinds:

- OBJECT — object identity plus property values;
- RELATION — typed link/adjacency between object identities;
- OBJECT_SET_OR_QUERY_EXPRESSION — composable object collection/query representation;
- RESULT — query/function/aggregate/derived result;
- ASYNC_STATE — loading/loaded/reloading/failed;
- EVENT_OR_OCCURRENCE — observable event/execution interaction when exposed.

Typed links remain first-class as a state role even though RELATION is not a peer top-level primitive.

## 3. OPERATION

OPERATION captures invocation and effect. This is the distinction that the original `TRANSITION` primitive was trying to express, but `TRANSITION` was too mutation-centric because public queries, functions, subscriptions and validation-only action calls are also invocations.

Effect classes currently supported by OFFICIAL witnesses:

- READ — ObjectSet filter, traversal, set composition, page/iteration;
- COMPUTE — aggregation, query/function, derived computation;
- VALIDATE — action validation-only;
- WRITE — action execution/application;
- OBSERVE — ObjectSet subscription;
- APPLICATION_INTERACTION — Workshop variable/event bridge.

The noun naming an operation does not automatically determine hidden side effects. Only observed/documented effects are asserted.

## 4. CONSTRAINT

CONSTRAINT preserves the distinction between an operation and whether/how it is allowed.

Observed categories:

- SCHEMA — property/parameter/type shape;
- DOMAIN_VALIDATION — action validation result;
- ACCESS — OAuth client context, scopes, security metadata;
- CARDINALITY/MULTIPLICITY — typed relation multiplicity metadata;
- CAPABILITY — optional constraints discovered on particular public operations.

This avoids conflating authentication with business validation or hard-coding one third-party policy engine into the model.

# Major public behavior

## Object and link model

Object definitions expose API/RID identity, primary-key metadata, typed properties and named typed links. Link targets and multiplicity are represented publicly. ObjectSet traversal can pivot through links.

Required claim: typed object identity + typed relationship/traversal.

Not required: graph database, independent persistent link RID for every link, a specific history store.

## ObjectSet

ObjectSet is not equivalent to `Object[]`. The public OSDK surface supports composition and deferred behavior including:

```text
ObjectSet
  -> where/filter
  -> union
  -> intersect
  -> subtract
  -> link traversal/pivot
  -> aggregate
  -> fetch page / async iterate
  -> subscribe
```

The reconstruction therefore models ObjectSet as query/state semantics, with materialization only one operation over it.

## Actions

The public SDK exposes Action as a typed definition and action application as an operation. Critically, it distinguishes:

```text
VALIDATE_ONLY
       versus
VALIDATE_AND_EXECUTE
```

and can optionally return edits. Invalid validation is observable as structured action validation failure.

What is established: action definition, validation and execution are distinct public concepts.

What is not established: every possible Foundry mutation internally or externally must be action-gated, or one exact private transaction/side-effect order.

## Queries, functions and derived values

Public surfaces expose typed query definitions, ObjectSet aggregation/derived-property operations and broader Platform Functions execution APIs. These are separate from Action definitions/application.

What is established: computation/read surfaces are distinct from the typed Action surface.

What remains open: whether every capability named "function" is universally side-effect-free.

## Authorization

Authentication and authorization are independent of domain validation:

```text
OAuth / client / scope context
            |
            v
        OPERATION
            |
      action validation etc.
```

A request can therefore be invalid for access reasons and independently invalid according to action/schema semantics. The model does not assume OpenFGA, ABAC, RBAC or any particular internal policy technology.

## Async / subscription / application interaction

Public OSDK exposes subscription behavior. Workshop's custom application bridge makes state transitions such as loading, succeeded, reloading and failed explicit, and supports bidirectional value state plus configured event execution.

This is why async state is modeled explicitly rather than represented by nullable data.

# OSDK versus Platform SDK

This is one of the strongest official architectural boundaries visible from source:

```text
createClient(stack, ontologyRid, auth)
        ontology-bound OSDK

createPlatformClient(stack, auth)
        broader platform client
```

The platform SDK exposes Foundry/Gotham API namespaces and can be used without binding the client to one ontology. OSDK itself calls lower-level Foundry packages for operations such as Action application.

Therefore the exposed architecture is not "one ontology API." It is an ontology semantic programming surface operating alongside/over a broader platform API surface.

# Independent reconstruction comparison

## gura105/operational-ontology

Best minimal semantic reference. It sharpens objects/links/actions, business preconditions, action-gated writes, explicit state authority, write-back and audit behavior. Its authority/write-back ordering and storage mechanics are implementation choices, not Palantir facts.

## Przyval/openfoundry

Best Foundry-shaped emulator reference. It implements `/api/v2`-style ontology/object/ObjectSet/action/function/auth surfaces and concrete query/action behavior. Its gateway/service layout and local persistence are emulator choices.

## syzygyhack/open-foundry

Best broader architecture rival. It independently composes schema, query/API, action, security, sync and storage-provider layers, helping show which semantics survive different implementation technology.

## Additional cross-checks

- `pkupt/Ontic` independently reimplements a wide Foundry-like surface with DuckDB query pushdown and generated OSDK.
- `Aryan1718/operational-ontology` independently implements a supply-chain operational ontology with objects/links/functions/actions/permissions/audit/MCP.
- `fstech-digital/operational-ontology-framework` is conceptual rather than production code; its D+L+A decomposition served as a genuine rival representation.

Apparent mirrors/near-copies are not counted as independent evidence.

# Rival representation result

Initial candidate:

`THING / RELATION / TRANSITION / QUERY / POLICY / EVENT`

Failed ablation because QUERY, POLICY and EVENT did not need peer-primitive status.

D/L/A rival:

`DATA / LOGIC / ACTION`

Successfully demonstrated that the six-peer set was over-specified, but preserves S01-S10 only by recreating definition/instance, invocation and constraint distinctions inside those broad buckets.

Accepted distinguished roles:

`DEFINITION / STATE / OPERATION / CONSTRAINT`

A four-role necessity check confirms that deleting any distinction rather than merely renaming it loses REQUIRED behavior:

- no DEFINITION -> type/instance and definition/invocation distinctions disappear;
- no STATE -> objects/links/results/async states disappear;
- no OPERATION -> read/compute/validate/write/observe invocation semantics disappear;
- no CONSTRAINT -> access/validation/cardinality distinctions become implicit operation code.

# Remaining unknowns

These are explicitly preserved but non-blocking for the high-level denominator:

1. universal action-only business-write closure;
2. universal exposed source/ontology/derived state-authority taxonomy;
3. universal independent identity/history semantics for link instances;
4. universal purity restriction for all function/query capabilities;
5. exact private transaction/side-effect ordering;
6. private storage/query/index/event/service architecture.

T012 inverted the first four. Both plausible outcomes fit the same four roles and conservative routing, so none can currently alter the core model. T013 therefore rejects live probing at this target on value-of-information grounds.

# Routing rule

For any newly encountered public capability:

```text
1. Is it a schema/capability description?
      -> DEFINITION

2. Is it an identifiable/current/result/occurrence value?
      -> STATE

3. Is it something invoked/observed?
      -> OPERATION
      -> record its observed effect, do not infer from its name

4. Does it govern validity, permission, cardinality or capability?
      -> CONSTRAINT

5. Does it merely reveal private implementation technology?
      -> do not promote unless it changes a REQUIRED observable behavior

6. Does evidence disagree?
      -> preserve UNKNOWN; test whether opposite outcomes change roles/routing

7. If neither outcome changes roles/routing at current target:
      -> quarantine as compatibility detail and continue
```

# Completion statement

`HIGH_LEVEL_READY` means:

- the finite S01-S10 public-surface denominator is covered 10/10 with OFFICIAL witnesses;
- independent reconstruction agreements and disagreements have been separated;
- the original primitive model was falsified and repaired through rival/ablation testing;
- Palantir-specific public constraints are separated from generic operational-ontology design choices;
- opposite plausible outcomes for remaining decision-changing questions have been tested;
- no currently known unresolved question can force a different core primitive or mandatory routing rule for this high-level target;
- zero-value live probes were not executed.

It does **not** mean Foundry has been source-reconstructed internally, that the private architecture is known, or that an independent implementation would yet be API-compatible across the full platform.
