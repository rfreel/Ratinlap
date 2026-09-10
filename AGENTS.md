# AGENTS.md

## Purpose

Ratinlap reconstructs the public and observable architecture of Palantir Foundry-style operational ontology systems. The repository must remain understandable without chat history and must not present proprietary internals as known facts.

## Cold Start

1. Read AGENTS.md.
2. Read contracts/SCOPE.md, contracts/SEMANTICS.md, contracts/ACCEPTANCE.md.
3. Read tasks/QUEUE.jsonl.
4. Read only source/model files named by the selected task.
5. Execute one task to its artifact and completion condition.

## Roles

**COORDINATOR** owns writes to `tasks/QUEUE.jsonl` and `model/model.json`, assigns or claims work, validates artifacts, integrates model changes, and runs `scripts/check.py`.

**WORKER** reads canonical state, writes only the artifact named by its task, and returns proposed distinctions, model changes, and unknowns to the coordinator.

If no coordinator is running, one agent may perform both roles serially. Parallel workers require disjoint artifact paths and no canonical writes.

## Hard Rules

1. Search for an existing reconstruction before inventing one.
2. Public or observable behavior outranks guessed internals.
3. Separate official Palantir behavior, third-party reconstruction, and inference.
4. Never convert `UNKNOWN` into fact.
5. Prefer the smallest explanatory model; expand only when a residual requires it.
6. Every model-changing task records the distinction that changed.
7. One task has one deliverable and one explicit completion condition.
8. Do not dump sources; extract only semantics that can change the model or a decision.
9. Implementation is a hypothesis test, not evidence about Palantir internals.
10. External writes or probes require explicit authorization for that target.
11. Never claim coverage without naming the scope denominator.
12. A primitive is accepted only if removing or merging it loses a REQUIRED observable distinction.
13. Workers never write `model/model.json` or `tasks/QUEUE.jsonl`; only the coordinator integrates canonical state.
14. A task is not DONE until its declared artifact exists and its `done_when` condition is checkable from repository state.
15. Do not count two reconstructions as independent until source lineage has been checked.
16. Before closing a decision-changing UNKNOWN, construct the opposite plausible answer and verify whether it changes the model or routing.

## Task Execution

Task state is stored only in `tasks/QUEUE.jsonl`. A READY task may be claimed only when every dependency is DONE. ACTIVE requires an owner. DONE requires the declared artifact and a checkable completion result. BLOCKED names an external dependency or authorization boundary. UNKNOWN names the unresolved distinction and the discriminator needed to resume.

Worker completion returns:

```json
{"task_id":"T001","artifact":"reconstructions/example.md","observed_distinctions":[],"proposed_model_changes":[],"new_unknowns":[],"done_when_result":"PASS"}
```

## Model Changes

`model/model.json` is the canonical reconstructed model. Every accepted change must name affected scope IDs, evidence class, and the observable distinction gained, lost, merged, or split. The candidate primitives are falsifiable; do not protect them from rival representations.

## External Actions

Repository-local edits on the authorized Ratinlap project are allowed. Black-box probes, writes to external systems, credentials, production environments, or third-party accounts require separate authorization for that target.

## Completion

`BOOTSTRAP_COMPLETE` means the research workspace is structurally ready. `HIGH_LEVEL_READY` means the semantic acceptance contract passes. Never report the first as the second.
