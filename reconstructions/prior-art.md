# Prior art discovery

Task: T001
Status: DONE

## Search families

1. `Palantir Foundry alternative ontology`
   - Found `Przyval/openfoundry`, `u485349-coder/OpenFoundry`, `davidwwzhu/OpenFoundry-Ontology`, many apparent mirrors/copies, and related OpenFoundry variants.
   - New architecture/distinctions: Foundry-shaped API emulation; broader open operational-intelligence platform variants.

2. `"operational ontology" reference implementation`
   - Found `gura105/operational-ontology`, `Aryan1718/operational-ontology`, `fstech-digital/operational-ontology-framework`, and many repositories with near-identical names/content.
   - New architecture/distinctions: minimal action-gated operational ontology; independent supply-chain implementation; conceptual D+L+A governance reference.

3. `OSDK Foundry compatible implementation` / `Palantir Ontology SDK alternative`
   - Returned no new architecture beyond `Przyval/openfoundry` and obvious descendants/mirrors.
   - No new REQUIRED behavioral distinction.

4. `Foundry ObjectSet actions ontology`
   - No repository results.
   - No new REQUIRED behavioral distinction.

5. `Foundry digital twin open source ontology platform`
   - Found `syzygyhack/open-foundry`, `CWNApps/open-foundry-ontology`, and many same-family `open-foundry` repositories.
   - New architecture/distinctions: schema compiler + action pipeline + security + sync + storage SPI; domain-pack model.

6. `Palantir Foundry reverse engineered open source`
   - No repository results.
   - No new REQUIRED behavioral distinction.

7. `"Foundry-style" ontology`
   - Found `pkupt/Ontic` plus narrow domain examples.
   - `Ontic` is a materially useful independent reimplementation: ontology metadata, ObjectSet-to-SQL pushdown, actions, generated OSDK, ABAC, data plane, app surface, AIP/MCP.

8. Follow-up review of named candidates and README similarity
   - `atypical-inc/operational-ontology` is textually the same gura105 reference family and is not counted as independent.
   - `davidwwzhu/OpenFoundry-Ontology` shares the same long-form OpenFoundry marketing README as `u485349-coder/OpenFoundry` with minor licensing/documentation changes; treat as same/derived family until contrary evidence.
   - `CWNApps/open-foundry-ontology` repeats the architecture, package taxonomy, and domain-pack vocabulary of the `syzygyhack/open-foundry` family; treat as same/derived family until contrary evidence.
   - Many `OpenFoundry` and `open-foundry` repositories returned by search have near-identical names, sizes, or README text; do not count them as independent without lineage proof.

## Independence groups retained

| Group | Representative | Classification | Why retained |
|---|---|---|---|
| official-palantir | `palantir/osdk-ts`, `palantir/foundry-platform-typescript`, official examples/integrations | OFFICIAL | Public Palantir contract surface; one authority lineage, not independent votes. |
| gura105-operational-ontology | `gura105/operational-ontology` | RECONSTRUCTED | Minimal executable definition of objects, links, actions, ownership, write-back, audit and failure semantics. |
| przyval-openfoundry | `Przyval/openfoundry` | RECONSTRUCTED | Explicit local Foundry emulator with `/api/v2`, ObjectSets, actions, OAuth, services and SDK tests. |
| syzygyhack-open-foundry | `syzygyhack/open-foundry` | RECONSTRUCTED | Larger schema-driven ontology/action/security/sync/storage implementation. |
| aryan-operational-ontology | `Aryan1718/operational-ontology` | RECONSTRUCTED | Different stack and supply-chain vertical; explicit objects/links/functions/actions/permissions/audit/MCP. |
| ontic | `pkupt/Ontic` | RECONSTRUCTED | Independent minimal Foundry reimplementation; DuckDB data plane, SQLite metadata, ObjectSet query pushdown, actions, OSDK generation, ABAC, applications and MCP. |
| fstech-dla-reference | `fstech-digital/operational-ontology-framework` | RECONSTRUCTED-CONCEPTUAL | No production code; useful only as a rival conceptual decomposition: Data + Logic + Action with explicit state/governance. |
| generic-openfoundry-marketing | `u485349-coder/OpenFoundry` | RECONSTRUCTED-LOWER-WEIGHT | Broad operational-intelligence platform; current README is product-level and less useful for semantic reconstruction than the executable candidates above. |

## Lineage decisions

- Count repositories as independent only when architecture/code/history establishes materially distinct implementation lineage.
- Exact or near-exact README/code copies, mirrors, renamed ports and obvious descendants collapse into one independence group.
- GitHub `fork=false` is insufficient evidence of independence because copied repositories can be recreated rather than forked.
- Third-party agreement never promotes a claim to OFFICIAL; it only increases confidence that a distinction is common among reconstructions.

## Saturation result

The discovery pass is saturated for the high-level target, not for all GitHub. After the last architecture-bearing discovery (`pkupt/Ontic`), the remaining reviewed results were narrow domain examples or apparent mirrors/descendants and introduced no new REQUIRED primitive class. Two materially different families (`reverse engineered open source` and direct `ObjectSet/actions` search) produced no new architecture; later `Foundry-style` search added Ontic but subsequent candidate review added no new primitive category beyond data/model, query, action, policy, event, integration, storage and presentation boundaries.

Promote for deep inspection now: `gura105/operational-ontology`, `Przyval/openfoundry`, `syzygyhack/open-foundry`, official Palantir repos. Retain `Aryan1718/operational-ontology` and `pkupt/Ontic` as independent rivals/cross-checks for later disagreement testing. Do not spend the critical path on apparent OpenFoundry mirrors unless a disagreement requires lineage resolution.
