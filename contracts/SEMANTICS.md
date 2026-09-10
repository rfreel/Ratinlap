# Semantics Contract

The initial semantic vocabulary is a reconstruction hypothesis, not an authority claim.

- `THING`: identifiable object or concept.
- `RELATION`: typed connection between elements.
- `TRANSITION`: operation that changes state or interpretation.
- `QUERY`: read-only operation over state.
- `POLICY`: authorization, visibility, or business-rule constraint.
- `EVENT`: observable occurrence emitted by or consumed by the system.

Do not add a primitive while an existing primitive can preserve the observable distinction without loss. Conversely, do not preserve a small vocabulary by forcing observably different behavior into one primitive.

Before `HIGH_LEVEL_READY`, fit at least one materially different rival representation to the same REQUIRED observations. For each core primitive, attempt removal or merge. A primitive is necessary only when the ablation loses at least one REQUIRED observable distinction or changes correct routing.

Names are not mechanisms. Similar terminology across implementations is not evidence that their hidden implementation is the same.
