# Task Protocol

`tasks/QUEUE.jsonl` is canonical current task state. It contains exactly one current record per task ID; it is not an event log.

## State machine

```text
READY -> ACTIVE -> DONE
             \-> BLOCKED
             \-> UNKNOWN -> READY
```

## Record schema

Every task contains:

```json
{"id":"T001","state":"READY","depends_on":[],"artifact":"reconstructions/example.md","deliverable":"...","done_when":"...","scope_ids":["S01"],"owner":null}
```

## Rules

- ACTIVE requires a non-null owner.
- READY may be claimed only when every dependency is DONE.
- Parallel tasks must have disjoint artifact paths.
- DONE requires the declared artifact to exist and the `done_when` condition to be checkable from repository state.
- BLOCKED names an external dependency or authorization boundary.
- UNKNOWN names the unresolved distinction and discriminator required to resume.
- Workers never edit the queue. The COORDINATOR rewrites the current record when state changes.

## Worker handoff

A completed worker returns exactly the task outcome needed for coordinator integration:

```json
{"task_id":"T001","artifact":"reconstructions/example.md","observed_distinctions":[],"proposed_model_changes":[],"new_unknowns":[],"done_when_result":"PASS"}
```

This object is a handoff, not a third canonical state store.
