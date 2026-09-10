# Opposite-outcome analysis

Task: T012
Status: DONE

Each previously decision-changing unknown is inverted. The test is not whether one answer is more attractive; it is whether either plausible answer forces a different core primitive or mandatory high-level routing rule.

# U-A — universal action-only write closure

## Outcome A1 — YES, every business-object mutation is action-gated

Model consequence:

```text
OPERATION(effect=WRITE, domain_state=true)
    -> must reference Action DEFINITION
    -> validation/constraints
    -> STATE delta
```

Primitive change: none.
Routing change from current robust model: one additional constraint on a subset of WRITE operations.

## Outcome A2 — NO, other business-object mutation surfaces coexist

Model consequence:

```text
OPERATION(effect=WRITE)
    -> action family OR other exposed write family
    -> each family carries its own constraints/effects
```

Primitive change: none.
Current routing already supports this.

Decision: quarantine `all_writes_action_gated` as an optional/unknown constraint. Neither outcome changes the four-role architecture. Do not block high-level closure on it.

# U-B — mandatory source/ontology/derived authority taxonomy

## Outcome B1 — YES, public state declares authority and write-back routing

Model consequence:

```text
DEFINITION/STATE.authority
    = SOURCE | ONTOLOGY | DERIVED | ...

WRITE OPERATION
    constrained/routed by authority metadata
```

Primitive change: none. Authority is definition/state metadata plus a CONSTRAINT on WRITE routing.

## Outcome B2 — NO universal public taxonomy

Model consequence:

State definitions need no mandatory authority field. Integrations/write-back remain capability-specific OPERATIONs and CONSTRAINTs.

Primitive change: none.
Current robust routing supports this.

Decision: authority taxonomy is not foundational at current target. If official evidence later establishes it, add metadata/constraint without changing primitives.

# U-C — independent link-instance identity/history

## Outcome C1 — YES, every relevant link instance has its own persistent identity/history

Model consequence:

```text
STATE(kind=RELATION) {
  id,
  type,
  from,
  to,
  properties,
  history...
}
```

Primitive change: none.
Routing change: traversal may address relation state directly and history becomes an optional read capability.

## Outcome C2 — NO, typed adjacency/multiplicity is sufficient for some public links

Model consequence:

```text
STATE(kind=RELATION) {
  type,
  from,
  to,
  multiplicity...
}
```

Identity/history fields are optional/not guaranteed.

Primitive change: none.
Current canonical relation role already assumes only typed endpoints/traversal.

Decision: retain relation as a distinguished STATE kind, with identity/history capability-dependent. Either outcome fits.

# U-D — function/query purity

## Outcome D1 — YES, functions/queries are guaranteed read-only

Model consequence:

```text
function/query OPERATION.effect in {READ, COMPUTE}
action OPERATION.effect includes WRITE
```

Primitive change: none.
Routing gets a stronger invariant on operation definitions.

## Outcome D2 — NO, some function-like public capability can perform side effects

Model consequence:

```text
OPERATION.effect is declared/observed per operation
noun "function" does not determine effect
```

Primitive change: none.
Current robust routing already supports it.

Decision: do not encode universal purity unless official evidence demands it. Known ObjectSet/query operations remain READ/COMPUTE; unknown function effects do not contaminate that evidence.

# Cross-case result

The opposite outcomes agree on the architecture:

```text
DEFINITION
    describes shape/capability

STATE
    holds identifiable/current/historical/query/async relation state

OPERATION
    has declared/observed effect:
    READ | COMPUTE | VALIDATE | WRITE | OBSERVE | APPLICATION_INTERACTION

CONSTRAINT
    limits an operation/state:
    SCHEMA | DOMAIN | ACCESS | CARDINALITY | optional authority/capability
```

The unknowns vary attributes and routing constraints *inside* those roles, not the roles themselves.

# Acceptance consequence

`opposite_outcome_checks_complete = true` is justified for every currently known decision-changing unknown.

After inversion, none of U-A through U-D can force a new core primitive or invalidate the public-surface routing because the canonical model deliberately does not overclaim the stronger branch. They remain useful compatibility/reconstruction questions, but they no longer block `HIGH_LEVEL_READY` for S01-S10.
