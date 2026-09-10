# Reconstruction Prewalk

Work outside-in and preserve the finite denominator.

1. Freeze the REQUIRED scope denominator in `contracts/SCOPE.md`.
2. Run bounded prior-art discovery and lineage-deduplicate reconstruction sources.
3. Establish source inventory, pinned revisions, licensing, and provenance.
4. The COORDINATOR assigns source-inspection tasks with disjoint artifact paths.
5. Workers extract public nouns/types, operations, failures, and transitions without editing canonical model state.
6. The COORDINATOR compares lineage-distinct reconstructions and checks proposed shared distinctions against official Palantir public surfaces.
7. Compile the smallest candidate model that explains REQUIRED observable behavior.
8. Construct a materially different rival representation from the same observations; ablate or merge candidate primitives and identify any lost REQUIRED distinction.
9. Record disagreements as UNKNOWN rather than averaging them away.
10. For each decision-changing UNKNOWN, construct the opposite plausible answer and test whether model structure or routing changes.
11. Probe only disagreements whose plausible outcomes can change the high-level model.
12. Recompute coverage against S01-S10.
13. Stop when remaining unknowns cannot change the core model under any currently plausible answer.

## Routing

```text
prior art -> source inspection -> shared distinctions
                              \-> disagreements
shared distinctions + disagreements -> rival model
                                \-> Palantir-specific constraints
rival model + Palantir constraints -> candidate model review
candidate model -> high-value unknowns -> opposite outcomes -> probes
candidate model + resolved decision boundaries -> high-level synthesis
```

BOOTSTRAP is preparation.
HIGH_LEVEL_READY is a semantic result.
Never report the first as the second.
