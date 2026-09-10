# Canonical model v0 review

Task: T010
Status: DONE

This is the coordinator review immediately before integrating `model/model.json` v0. It uses only distinctions accepted by T005-T009.

# Primitive change

Bootstrap candidate:

`THING / RELATION / TRANSITION / QUERY / POLICY / EVENT`

Accepted v0 basis after rival/ablation testing:

`DEFINITION / STATE / OPERATION / CONSTRAINT`

Evidence class: INFERRED representation over OFFICIAL observations.
Scopes: S01-S10.

Why:

- `QUERY` is an OPERATION with effect `READ|COMPUTE`.
- action invocation is an OPERATION with effect `WRITE` or `VALIDATE`.
- subscription/event interaction is an OPERATION/STATE occurrence rather than a peer primitive.
- policy, authorization, validation, precondition and cardinality fit a generalized CONSTRAINT role with distinct subtypes.
- typed links remain first-class as `STATE.kind=RELATION`; no requirement is lost by not making RELATION a top-level metaphysical primitive.
- definition versus runtime state remains explicit rather than hiding schema and instances in one generic data bucket.

Primitive necessity result: PASS relative to tested rivals. D/L/A showed six peers were unnecessary; the four-role model retains distinctions D/L/A obscures.

# Concepts admitted

| Concept | Role | Evidence | Scopes |
|---|---|---|---|
| ontology | DEFINITION container/context | OFFICIAL | S01,S09 |
| object_type | DEFINITION | OFFICIAL | S01,S02 |
| interface | DEFINITION | OFFICIAL | S01,S02 |
| property | DEFINITION | OFFICIAL | S02 |
| link | STATE kind=RELATION plus link definition metadata | OFFICIAL | S03 |
| object | STATE kind=OBJECT | OFFICIAL | S01,S02 |
| object_set | STATE kind=OBJECT_SET/QUERY_EXPRESSION | OFFICIAL | S04 |
| action | DEFINITION + OPERATION invocation | OFFICIAL | S05 |
| query | DEFINITION + OPERATION effect=READ/COMPUTE | OFFICIAL | S04,S06 |
| function | OPERATION effect=COMPUTE at platform boundary | OFFICIAL | S06,S09 |
| derived_value | STATE kind=RESULT | OFFICIAL | S06 |
| auth_context | CONSTRAINT/context | OFFICIAL | S07 |
| async_state | STATE kind=ASYNC_STATE | OFFICIAL | S08,S10 |
| event_occurrence | STATE kind=EVENT_OR_OCCURRENCE | OFFICIAL | S08,S10 |
| ontology_client | application interface over ontology-bound definitions/operations | OFFICIAL | S09,S10 |
| platform_client | application interface over broader platform operations | OFFICIAL | S09,S10 |

# Relations admitted

These are semantic edges in the reconstruction, not claims about physical graph storage:

- definition `HAS_PROPERTY` property definition — OFFICIAL — S02
- object type `HAS_LINK` link definition — OFFICIAL — S03
- link state `FROM/TO` object identities — OFFICIAL/INFERRED from typed traversal semantics — S03
- object state `INSTANCE_OF` object-type definition — INFERRED from OFFICIAL type/instance API distinction — S01,S02
- action definition `HAS_PARAMETER` parameter definitions — OFFICIAL — S05
- action definition `MAY_MODIFY` entity types — OFFICIAL metadata — S05
- query definition `HAS_PARAMETER/RETURNS` typed data — OFFICIAL — S04,S06
- ontology client `BOUND_TO` ontology RID — OFFICIAL — S09
- platform client `CALLS` platform namespaces independent of one ontology — OFFICIAL — S09
- application bridge `EXCHANGES` Workshop values/events — OFFICIAL — S08,S10

# Operations admitted

- `filter_object_set` — READ — OFFICIAL — S04
- `union_object_sets` — READ — OFFICIAL — S04
- `intersect_object_sets` — READ — OFFICIAL — S04
- `subtract_object_sets` — READ — OFFICIAL — S04
- `traverse_link` / pivot — READ — OFFICIAL — S03,S04
- `aggregate_object_set` — COMPUTE — OFFICIAL — S04,S06
- `fetch_page` / async iteration — READ — OFFICIAL — S04,S08
- `subscribe_object_set` — OBSERVE — OFFICIAL — S08
- `validate_action` — VALIDATE — OFFICIAL — S05
- `apply_action` — WRITE — OFFICIAL — S05
- `batch_apply_action` — WRITE — OFFICIAL — S05
- `execute_function/query` — COMPUTE — OFFICIAL — S06,S09
- `set_workshop_value_state` — WRITE at application bridge — OFFICIAL — S08,S10
- `execute_workshop_event` — OBSERVE/WRITE interaction at application bridge — OFFICIAL — S08,S10

# Constraint classes admitted

- SCHEMA: object/action/query parameter/property shape — OFFICIAL — S01-S06
- DOMAIN_VALIDATION: action validation result — OFFICIAL — S05
- ACCESS: OAuth/scopes/security metadata — OFFICIAL — S07
- CARDINALITY/MULTIPLICITY: link multiplicity is official metadata; exact enforcement semantics remain narrower UNKNOWN — OFFICIAL/PARTIAL — S03

No particular authorization engine or business-precondition language is admitted as Palantir-specific.

# Observable states admitted

- async `LOADING`
- async `SUCCEEDED/LOADED`
- async `RELOADING`
- async `FAILED`
- action validation `VALID|INVALID`
- action application may return edits or no edits according to requested mode
- ObjectSet result can be fetched/paged/subscribed

All are OFFICIAL public/application semantics. Exact internal action execution lifecycle is not asserted.

# Invariants admitted

I01 OFFICIAL: Object definitions have explicit identity/property metadata; object and definition roles are distinct.

I02 OFFICIAL: Typed links and traversal are represented in the public ontology programming surface.

I03 OFFICIAL: ObjectSet supports compositional operations; it is not equivalent to a pre-materialized array.

I04 OFFICIAL: Action validation-only and validation+execution are distinguishable public modes.

I05 OFFICIAL: Authentication/authorization context exists independently of domain/action parameter validation.

I06 OFFICIAL: Ontology-bound OSDK and standalone/general Platform SDK are distinguishable interfaces.

I07 OFFICIAL: Async/loading/reloading/failure and subscription/event behavior are application-observable distinctions.

I08 INFERRED: Physical storage/service technology is not part of the required high-level model because official contracts do not expose it and independent reconstructions vary it while preserving the public roles.

# Claims deliberately excluded

- universal action-only write closure across every Foundry mutation;
- exact property authority/write-back taxonomy;
- universal link-instance persistent identity/history;
- universal function purity;
- exact action side-effect commit order;
- specific database/graph/event technology;
- specific service decomposition;
- universal audit implementation/default visibility.

These either remain unknown or are below the high-level target.

# Coverage update

T005 found at least one OFFICIAL public witness for every REQUIRED scope S01-S10. Under the explicit denominator, each is now `COVERED` at the **high-level public programming-model target**.

This does not mean exhaustive API compatibility. The denominator is S01-S10, not all Foundry features/endpoints.

# Acceptance update before remaining tasks

- `bootstrap_complete`: true
- `rival_model_checked`: true
- `high_level_ready`: false until T011-T014 complete
- `opposite_outcome_checks_complete`: false until T012

Coordinator integration may now update `model/model.json` to v0.2 / status `RECONSTRUCTING` with the four-role basis and S01-S10 coverage `COVERED`.
