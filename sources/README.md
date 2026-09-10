# Sources

`sources/manifest.json` contains source seeds, not a complete corpus.

Before a source supports a reconstruction claim, pin its revision and verify its license or usage status. Prior-art discovery must use materially different search families such as Foundry emulator/clone/alternative, operational ontology reference implementation, Ontology SDK compatible implementation, and ObjectSet/action implementations.

Stop broad discovery only after two consecutive materially different search families yield no new architecture or REQUIRED behavioral distinction. This is a saturation heuristic, not proof that no other source exists.

For third-party reconstructions, record `derived_from` and `independence_group`. Forks, copied descendants, ports, or shared upstream lineage do not count as independent evidence merely because they live in different repositories.

Do not copy restricted-license implementation material into the clean reconstruction. Public availability and open-source licensing are separate questions.
