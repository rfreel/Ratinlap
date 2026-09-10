# Rival representation and primitive ablation

Task: T008
Status: DONE

The bootstrap candidate used six peer primitives:

`THING / RELATION / TRANSITION / QUERY / POLICY / EVENT`

That set is not accepted merely because it can encode the evidence. This task fits materially different representations to the same REQUIRED observations and asks which distinctions disappear when candidate primitives are merged.

# Rival A — Data / Logic / Action

Inspired by, but not dependent on, the FSTech conceptual decomposition.

```text
DATA
  definitions/types
  object instances/properties
  typed links
  ObjectSet expressions/results
  execution/loading/history records

LOGIC
  query expressions
  derived computations
  validation
  business preconditions
  authorization/visibility constraints

ACTION
  action invocation
  event execution
  subscription observation
  state mutation
  external side effect
```

## Fit against S01-S10

- S01 type/instance split: represented as two DATA roles (`definition`, `instance`).
- S02 objects/properties: DATA.
- S03 links/traversal: link DATA + traversal LOGIC.
- S04 ObjectSet/filter/aggregate: DATA expressions + LOGIC operators.
- S05 actions/validation/effects: ACTION governed by LOGIC.
- S06 functions/derived values: LOGIC returning DATA.
- S07 auth: LOGIC constraining ACTION/read operations.
- S08 async/loading/events: DATA state + ACTION/observation occurrence.
- S09 OSDK/Platform boundary: interface/boundary metadata around DATA/LOGIC/ACTION; no new primitive required.
- S10 application interaction: applications invoke ACTION/LOGIC and consume DATA; no new primitive required.

Result: Rival A can encode every REQUIRED observation found so far with only three top-level buckets. Therefore the six bootstrap primitives are not irreducible.

Weakness: `DATA` is too broad. It hides the important distinction between a typed relationship and an object's properties, and it makes callable operations look like logic versus action based on effect rather than a shared invocation concept.

# Rival B — Definition / State / Operation / Constraint

A second representation changes the primitive basis more aggressively while preserving the public programming distinctions:

```text
DEFINITION
  describes allowable shape/capability
  object type / interface / action definition / query definition / property metadata

STATE
  identifiable current or historical value
  object / property value / link / ObjectSet expression / loading state / execution result

OPERATION
  callable or observable behavior
  kind = READ | COMPUTE | WRITE | OBSERVE
  ObjectSet filter/traverse/aggregate
  query/function
  action validate/apply
  subscribe/event execution

CONSTRAINT
  predicate or permission governing an operation/state
  schema/type validity
  action validation/precondition
  authorization/visibility
  cardinality
```

Boundaries such as OSDK versus Platform API and Application versus Workshop are not primitives; they are interfaces grouping definitions and operations.

Events are occurrences/results in STATE produced or consumed by `OBSERVE`/`WRITE` operations. Relations are a distinguished STATE kind with endpoints and type; they need not be a top-level metaphysical primitive to remain first-class in the model.

## Fit against S01-S10

All ten REQUIRED surfaces map without exception:

| Scope | Rival B representation |
|---|---|
| S01 | DEFINITION vs STATE |
| S02 | object STATE conforms to DEFINITION |
| S03 | link STATE + traversal OPERATION + cardinality CONSTRAINT |
| S04 | ObjectSet STATE/expression + READ/COMPUTE OPERATION |
| S05 | action DEFINITION + validate/write OPERATION + CONSTRAINT + resulting STATE |
| S06 | query/function DEFINITION + COMPUTE OPERATION + derived STATE |
| S07 | auth/visibility CONSTRAINT around OPERATION |
| S08 | loading/execution/event STATE + OBSERVE OPERATION |
| S09 | grouped public interfaces over DEFINITION/OPERATION |
| S10 | application invokes exposed OPERATION and receives STATE |

Result: Rival B preserves the evidence with four orthogonal roles and makes fewer assumptions than the six-peer bootstrap candidate.

# Ablation / merge tests on original candidate

## Remove QUERY

Merge QUERY into a generic operation/transition with `effect=READ|COMPUTE`.

Lost REQUIRED observation: none. We can still distinguish read from write by effect classification.

Verdict: `QUERY` is not necessary as a peer primitive.

## Remove EVENT

Represent an event as an occurrence/result STATE/THING with relations to the operation that emitted/consumed it; subscription is an OBSERVE operation.

Lost REQUIRED observation: none. Workshop event execution and ObjectSet subscriptions remain expressible.

Verdict: `EVENT` is not necessary as a peer primitive.

## Remove POLICY

Represent authorization/visibility/business rules as typed constraints/predicates attached to definitions/operations.

Lost REQUIRED observation: none, provided the model retains the distinction between access constraints and business/validity constraints.

Verdict: `POLICY` is not necessary as a peer primitive; `CONSTRAINT` is the more general role.

## Remove TRANSITION

If only THING/RELATION remain, action invocation, validation-only versus execution, function/query calls and temporal state changes must be reified as THINGs with ad hoc relation patterns. The fact that the same definition is *invoked* with inputs and yields a result/effect ceases to have one explicit role.

Lost REQUIRED distinction: operation/invocation semantics across S04-S06 and S08.

Verdict: some operation/transition primitive is necessary. Rename to `OPERATION` because not every public invocation mutates state.

## Remove RELATION

Links can technically be reified as THING/STATE records with `from`, `to`, `type` fields. That preserves data but erases typed adjacency/traversal as a distinguished structural role unless every consumer rediscovers the endpoint convention.

Lost REQUIRED distinction: typed relation/traversal semantics become implicit rather than model-governed in S03.

Verdict: retain relation as an explicit **state kind/role**, but top-level primitive status is not required if STATE has a mandatory `kind=RELATION` contract.

## Remove THING

A universal STATE record could encode objects and definitions, but then stable identity of objects/definitions versus transient operation results is no longer explicit without recreating an entity role inside STATE.

Lost REQUIRED distinction: identifiable semantic object/type roles across S01-S03 become implicit.

Verdict: the concept survives better as `STATE` + identity/schema roles than as undifferentiated THING.

# Ablation result

The six-peer candidate fails its own necessity criterion.

Recommended canonical basis:

```text
DEFINITION
STATE
OPERATION
CONSTRAINT
```

Required distinguished subroles, not peer primitives:

```text
STATE.kind:
  OBJECT
  RELATION
  OBJECT_SET
  RESULT
  EVENT_OR_OCCURRENCE
  ASYNC_STATE

OPERATION.effect:
  READ
  COMPUTE
  WRITE
  OBSERVE

CONSTRAINT.kind:
  SCHEMA
  DOMAIN
  ACCESS
  CARDINALITY
```

This basis explains why Palantir exposes ObjectType/Action/Query *definitions*, object/link/ObjectSet *state*, callable query/action/subscription *operations*, and validation/auth/cardinality *constraints* without claiming a specific internal representation.

# Why not adopt D/L/A directly?

D/L/A is a successful rival: it falsifies the necessity of the six-peer model. But its `DATA` and `LOGIC` buckets collapse distinctions the official API makes explicit—definition versus instance, operation definition versus invocation, and typed link adjacency versus arbitrary data. Rival B preserves those distinctions with only one additional role and therefore wins for this reconstruction target.

# Acceptance record

`rival_model_checked = true` is justified for the high-level model because two materially different representations were fit to the same S01-S10 observations and the bootstrap primitive set was actually changed by the result. This is not a claim that four roles are mathematically unique; it is the smallest tested basis currently preserving the REQUIRED distinctions without encoding them as ad hoc tags.
