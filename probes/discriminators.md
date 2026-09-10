# Discriminating probes

Task: T013
Status: DONE

## Routing decision

No live black-box probe is required for the current S01-S10 high-level target.

Reason: T012 tested both plausible outcomes of every previously decision-changing unknown. Each outcome fits the same canonical `DEFINITION / STATE / OPERATION / CONSTRAINT` roles and the same conservative routing once stronger universal claims are withheld. Therefore executing a live probe cannot change `HIGH_LEVEL_READY`; its value is compatibility/detail, not high-level architecture.

No authorized Palantir test stack or tenant was supplied for black-box probing in this task. Public-source inspection is authorized; live external probing is not assumed.

This is a VOI stop, not a claim that the questions are answered.

## Deferred discriminator D-P1 — universal action-only write closure

Execution status: EXCLUDED FROM CURRENT RUN

Rival predictions:
- A: all public business-object mutations resolve to an Action definition/invocation.
- B: at least one supported business-object state mutation exists outside Action semantics.

Minimum input if later authorized: one disposable object type/object plus an inventory of official mutation APIs in an authorized development stack.

Observation: whether a non-action mutation can alter the same business object state without creating/invoking an Action.

Routing consequence: add or omit an `ALL_DOMAIN_WRITES_REQUIRE_ACTION` constraint on WRITE operations. No primitive change.

Current decision value: zero for high-level target; positive for strict compatibility/security semantics.

## Deferred discriminator D-P2 — exposed authority/write-back taxonomy

Execution status: EXCLUDED FROM CURRENT RUN

Rival predictions:
- A: property/action metadata exposes source/ontology/derived authority and changes routing/failure semantics.
- B: no universal public authority classification is exposed.

Minimum input: one object type with source-backed data plus one writable property/action on an authorized stack, accompanied by public metadata/API inspection.

Observation: exposed ownership metadata and observable direction/failure of a write-back.

Routing consequence: optional authority CONSTRAINT becomes mandatory on a subset of WRITE definitions. No primitive change.

Current decision value: zero for high-level target; positive for integration fidelity.

## Deferred discriminator D-P3 — link-instance identity/history

Execution status: EXCLUDED FROM CURRENT RUN

Rival predictions:
- A: link instances expose stable independent identity/properties/history.
- B: some link surfaces expose only typed adjacency/target/multiplicity.

Minimum input: two disposable objects with repeated relationships over time, if the target ontology supports such a link type.

Observation: whether the API returns link-instance identity/history independently of endpoint objects.

Routing consequence: require or leave optional `STATE(kind=RELATION).id/history`. No primitive change.

Current decision value: zero for high-level target; positive for link compatibility.

## Deferred discriminator D-P4 — function/query side-effect restriction

Execution status: EXCLUDED FROM CURRENT RUN

Rival predictions:
- A: function/query contracts are guaranteed not to mutate business ontology state.
- B: at least one function-like capability may produce externally visible side effects or state mutation.

Minimum input: public function metadata plus a disposable authorized execution target.

Observation: whether a function/query invocation can produce a business-state delta that is not an Action edit.

Routing consequence: constrain function OPERATION effects to READ/COMPUTE or allow effect to be capability-declared. No primitive change.

Current decision value: zero for high-level target; positive for strict operation classification.

# Probe gate

A deferred probe is promoted to execution only when all are true:

1. the user has authorized the actual target system/account;
2. the observation cannot be obtained more cheaply from official public contracts;
3. rival predictions differ;
4. the result changes a currently requested decision, compatibility claim or implementation.

At the current target, no probe passes all four conditions. Zero-value probes are therefore excluded rather than executed for ceremony.
