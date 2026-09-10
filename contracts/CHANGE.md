# Change Contract

Canonical working state has exactly two single-writer files:

- `model/model.json`
- `tasks/QUEUE.jsonl`

Only the COORDINATOR integrates writes to those files. Workers write only their declared task artifact and return proposed changes through the worker handoff contract.

Every accepted model change records:

- affected scope IDs
- evidence class
- distinction gained, lost, split, or merged
- source or observation that motivates the change
- whether the change alters routing or acceptance status

Every model-changing task must name the scope IDs it may alter before execution.

A semantic primitive may be added, merged, or removed only with a named REQUIRED observable distinction showing why the change is necessary.

New directories, schemas, databases, frameworks, or orchestration layers require a concrete failure of the current structure. Prefer extending an existing contract or record type.

Historical evidence is not rewritten merely because the current model changes. Supersession should be explicit in the consuming artifact or model update.
