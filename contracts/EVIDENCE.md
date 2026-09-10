# Evidence Contract

Every reconstruction claim is classified as exactly one of:

- `OFFICIAL`: directly supported by Palantir public material.
- `OBSERVED`: produced by an authorized black-box observation.
- `RECONSTRUCTED`: implemented by an independent third-party reconstruction.
- `INFERRED`: derived from supported facts.
- `UNKNOWN`: unresolved.

Rules:

1. `UNKNOWN` is never silently promoted to another class.
2. `RECONSTRUCTED` consensus never becomes `OFFICIAL`.
3. Third-party agreement is counted only across lineage-distinct independence groups.
4. Forks, ports, copied code, generated descendants, or implementations derived from the same upstream source count as one independence group unless a discriminating difference establishes otherwise.
5. Every reconstruction source records `derived_from` and `independence_group`.
6. Popularity, stars, prose confidence, or naming similarity do not increase confidence in Palantir behavior.
7. A claim used to mark a REQUIRED scope `COVERED` needs at least one `OFFICIAL` or `OBSERVED` supporting behavior.
