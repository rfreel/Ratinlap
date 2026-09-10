# Canonical Model

`model/model.json` is the canonical reconstructed semantic model. Workers never edit it directly. They propose model changes in their task artifact; the COORDINATOR integrates accepted changes.

Every accepted model change must name:

- affected scope IDs
- evidence class
- the observable distinction gained, lost, split, or merged
- the motivating source or observation
- whether routing or acceptance changes

The initial primitive list is a candidate representation. It remains falsifiable until rival-model and ablation checks are complete.

`model/unknowns.jsonl` stores unresolved questions whose plausible answers can change model structure or routing. Closing a decision-changing unknown requires testing the opposite plausible answer first.
