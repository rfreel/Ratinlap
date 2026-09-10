# Acceptance Contract

## BOOTSTRAP_COMPLETE

True only when all of the following hold:

- the agreed repository structure exists
- contracts are populated
- `tasks/QUEUE.jsonl` is valid
- source seeds are recorded
- `model/model.json` parses and covers every REQUIRED scope ID
- `scripts/check.py .` passes

BOOTSTRAP_COMPLETE means the research workspace is ready. It is not a claim that the architecture has been reconstructed.

## HIGH_LEVEL_READY

True only when all of the following hold:

1. Every REQUIRED scope ID is `COVERED`, `PARTIAL`, or `UNKNOWN`; none is silently absent.
2. Every `COVERED` scope ID has at least one OFFICIAL or OBSERVED supporting behavior.
3. Every major public operation inside a REQUIRED scope has a QUERY/TRANSITION interpretation or is explicitly UNKNOWN.
4. Every core primitive survives ablation/merge because removing it loses a REQUIRED observable distinction or changes correct routing.
5. At least one materially different rival representation has been fit to the same REQUIRED observations and its differences are recorded.
6. Third-party reconstruction agreements are grouped by lineage and are not treated as proof of Palantir internals.
7. Reconstruction disagreements are explicit.
8. Palantir-specific public constraints are separated from generic operational-ontology structure.
9. Every remaining decision-changing UNKNOWN has had the opposite plausible answer tested for whether it changes model structure or routing.
10. No remaining UNKNOWN can currently change the core primitive set or high-level routing under a plausible answer.
11. Coverage is reported as `covered_required / total_required`, with PARTIAL and UNKNOWN listed separately.
12. Every DONE task has its artifact and checkable completion result.
13. `scripts/check.py .` passes.

A high coverage percentage alone is insufficient. One unresolved decision-changing scope item blocks HIGH_LEVEL_READY.
