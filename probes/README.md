# Probe Contract

A probe exists to discriminate between rival explanations whose outcomes can change the high-level model or routing.

Every probe records:

- question
- affected scope IDs
- rival predictions
- minimum authorized input
- execution boundary and required authorization
- expected observation under each rival
- actual result when executed
- routing/model consequence

Do not run a probe merely because it is measurable. If every plausible result leaves the same high-level action or model unchanged, record the question as low value and do not spend the probe.

External systems are never probed without explicit authorization for that target.
