# Phase 3 prewalk — Foundry-shaped `/api/v2` adapter

## Target

Expose the Phase 2 executable semantic core through a deliberately small HTTP compatibility edge whose URL paths and supported wire forms are pinned to Palantir's public generated TypeScript SDK at revision `d1fbe480fa7d22c13862d90946d06f8910871570`.

The adapter must translate wire values into `runtime/reference.py`; it must not grow a second semantic engine.

## Official public paths in first slice

Supported in this phase:

```text
GET  /v2/ontologies/{ontology}/objectTypes/{objectType}
GET  /v2/ontologies/{ontology}/objects/{objectType}
GET  /v2/ontologies/{ontology}/objects/{objectType}/{primaryKey}
GET  /v2/ontologies/{ontology}/objects/{objectType}/{primaryKey}/links/{linkType}
POST /v2/ontologies/{ontology}/objectSets/loadObjects
POST /v2/ontologies/{ontology}/objectSets/aggregate
POST /v2/ontologies/{ontology}/actions/{action}/apply
```

`applyBatch`, async actions, search, temporary ObjectSets, multiple-object-type loads, media, timeseries, scenarios, branches, and transactions are deferred until the first slice is wire-stable.

## Supported ObjectSet wire grammar

Official tagged shapes admitted initially:

```text
{type:"base", objectType:string}
{type:"filter", objectSet:ObjectSet, where:SearchJsonQueryV2}
{type:"union", objectSets:ObjectSet[]}
{type:"intersect", objectSets:ObjectSet[]}
{type:"subtract", objectSets:ObjectSet[]}
{type:"searchAround", objectSet:ObjectSet, link:string}
```

For `SearchJsonQueryV2`, Phase 3 supports only the official equality form needed to exercise translation:

```text
{type:"eq", field:string, value:scalar}
```

Unsupported official variants return an explicit compatibility error; they are never guessed or silently approximated.

## Supported request/response subset

`loadObjects` accepts the official structural fields `objectSet`, `select`, optional `pageSize`, and optional `pageToken`. Phase 3 supports one-page responses only; a request carrying `pageToken` is rejected as unsupported rather than ignored.

`loadObjects` returns `{data:[...]}` with the object records projected through the requested `select`. No claim is made yet about exact RID metadata, null omission, vector-property selection, storage-v1 limits, or paging tokens beyond what this slice implements.

`aggregate` supports count and numeric sum over a translated ObjectSet. Exact broad Palantir aggregation grammar is deferred; the supported subset is declared in `compat/surface.json`.

`actions/{action}/apply` accepts the official top-level request shape:

```text
{
  parameters: {...},
  options?: {
    mode?: "VALIDATE_ONLY" | "VALIDATE_AND_EXECUTE",
    returnEdits?: string
  }
}
```

The response preserves the public distinction `validation.result = VALID|INVALID` and includes `edits` only when explicitly requested by a supported return-edits mode. A 200 response with `validation.result="INVALID"` is not converted into a transport error.

## Auth boundary

The semantic runtime already distinguishes ACCESS from PARAMETER and DOMAIN validation. This adapter does not pretend to implement Foundry OAuth. For testability, `X-Ratinlap-Actor` supplies the local actor identity. This header is explicitly non-compatible scaffolding and is quarantined in `compat/README.md`.

## Error policy

Three levels remain separate:

1. HTTP/wire errors: malformed JSON, route not found, unsupported wire variant;
2. access error: local actor is not permitted;
3. action validation result: parameter/domain invalidity expressed in the action validation body when the request reached that semantic operation.

No exact Palantir error payload is claimed unless pinned separately.

## Files

```text
compat/
  surface.json         machine-readable supported compatibility denominator
  wire.py              ObjectSet/action/object translation only
  server.py            pure dispatch + stdlib HTTP handler
  test_server.py       unit and HTTP conformance tests
  README.md            exact compatibility claims/non-claims
  report.json          executable compatibility report
scripts/
  serve_compat.py      one-command local server
  run_compat.py        one-command conformance report
model/
  api-compat-gaps.md   residuals after first wire slice
```

## Tasks

- T019: pin the first-slice public wire contract in `compat/surface.json`.
- T020: implement wire translators and pure request dispatcher over `ReferenceRuntime`.
- T021: add real HTTP tests and one-command server/report runners.
- T022: record compatibility residuals and decide the next expansion by value of information.

## Acceptance

`API_SLICE_READY` iff:

- all seven first-slice routes are exercised by tests;
- ObjectSet base/filter/union/intersect/subtract/searchAround translate into the existing runtime without duplicating evaluation semantics;
- equality filter uses the official tagged query shape;
- object type/list/get/link traversal return deterministic JSON for the local fixture;
- `loadObjects` consumes the declared subset and rejects unsupported paging rather than ignoring it;
- count and sum aggregation work over the same translated ObjectSet;
- action `VALIDATE_ONLY` is non-mutating;
- domain-invalid action returns HTTP 200 with `validation.result="INVALID"`;
- local access failure remains distinguishable;
- unknown routes/unsupported wire variants are explicit errors;
- `python -m unittest compat.test_server -v` passes;
- `python scripts/run_compat.py` writes `compat/report.json` with status PASS;
- `model/api-compat-gaps.md` names every intentionally deferred compatibility dimension.

## Stop condition

Do not expand to the full Foundry API merely because an endpoint exists. After this slice, choose the next surface by the smallest compatibility residual that would block a real OSDK smoke test.
