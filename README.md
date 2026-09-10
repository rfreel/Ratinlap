# Ratinlap

Ratinlap is a compact workspace for reconstructing the public and observable architecture of Palantir Foundry-style operational ontology systems without pretending to know proprietary internals.

## Current status

- `BOOTSTRAP_COMPLETE`: **true**
- `HIGH_LEVEL_READY`: **true** for the explicit S01-S10 public-surface denominator
- Required scope coverage: **10/10 COVERED**
- Canonical semantic roles: `DEFINITION / STATE / OPERATION / CONSTRAINT`

Read `docs/HIGH_LEVEL_MODEL.md` for the current reconstruction and its limits.

## Start here

1. `AGENTS.md` — operating and cold-start contract
2. `contracts/SCOPE.md` — finite S01-S10 denominator
3. `model/model.json` — canonical machine-readable model
4. `docs/HIGH_LEVEL_MODEL.md` — human-readable synthesis
5. `model/unknowns.jsonl` — explicitly quarantined remaining unknowns

The approved design is `docs/superpowers/specs/2026-09-10-ratinlap-reconstruction-design.md`; the bootstrap implementation plan is `docs/superpowers/plans/2026-09-10-ratinlap-bootstrap.md`.

Canonical working state lives only in `model/model.json` and `tasks/QUEUE.jsonl`. Everything else constrains, sources, tests, or projects those files.

`HIGH_LEVEL_READY` does not claim knowledge of Palantir's private storage, indexing, service topology, transaction implementation, or exhaustive API compatibility.
