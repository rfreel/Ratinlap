# Foundry-shaped compatibility slice

This directory is a thin translation edge over `runtime/reference.py`. It does not contain a second semantic engine.

## What is pinned to official public SDK source

At `palantir/foundry-platform-typescript` revision `d1fbe480fa7d22c13862d90946d06f8910871570`, the generated public SDK exposes the seven paths listed in `surface.json`. The official wire model also establishes:

- `ObjectSetBaseType { objectType }`;
- `ObjectSetFilterType { objectSet, where }`;
- union/intersection/subtract variants with `objectSets` arrays;
- `ObjectSetSearchAroundType { objectSet, link }`;
- `ApplyActionRequestV2 { parameters, options? }`;
- action modes `VALIDATE_ONLY | VALIDATE_AND_EXECUTE`;
- `AggregateObjectSetRequestV2` carries `aggregation: AggregationV2[]`, `objectSet`, and `groupBy: AggregationGroupByV2[]`;
- aggregate responses carry `accuracy` plus grouped `metrics`;
- `SyncApplyActionResponseV2` can contain `validation` and `edits`;
- `ValidationResult` is `VALID | INVALID`.

The OSDK client recognizes server objects via `__apiName` plus non-null `__primaryKey`, so this slice emits both.

## Deliberately partial wire grammar

Only equality filter, count/sum aggregation, one-page object loads, and modify-object action edit receipts are implemented. Unsupported variants are explicit errors.

`X-Ratinlap-Actor` is test scaffolding, not a Foundry header. OAuth and exact Foundry authorization scopes are not emulated yet.

## Run

```bash
python -m unittest compat.test_server -v
python scripts/run_compat.py
python scripts/serve_compat.py --port 8080
```

See `model/api-compat-gaps.md` before extending the surface.
