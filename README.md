# Ratinlap

Ratinlap is a compact workspace for reconstructing the public and observable architecture of Palantir Foundry-style operational ontology systems without pretending to know proprietary internals.

Start with `AGENTS.md`. The approved design is `docs/superpowers/specs/2026-09-10-ratinlap-reconstruction-design.md`; the bootstrap implementation plan is `docs/superpowers/plans/2026-09-10-ratinlap-bootstrap.md`.

Two completion states are intentionally separate:

- `BOOTSTRAP_COMPLETE`: contracts, task/model state, source seeds, and structural validation are ready.
- `HIGH_LEVEL_READY`: the semantic reconstruction acceptance contract passes.

Canonical working state lives only in:

- `model/model.json`
- `tasks/QUEUE.jsonl`

Everything else constrains, sources, tests, or projects those files.
