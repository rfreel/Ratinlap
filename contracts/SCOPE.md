# Scope Contract

The reconstruction denominator is finite and explicit. Changing a surface between REQUIRED, OPTIONAL, or EXCLUDED is a scope change and changes the meaning of completion.

Machine-readable scope declarations:

- S01 | REQUIRED | ontology identity and type-instance split
- S02 | REQUIRED | objects and properties
- S03 | REQUIRED | links and linked-object traversal
- S04 | REQUIRED | ObjectSet query filter and aggregation semantics
- S05 | REQUIRED | actions validation effects and visible failure states
- S06 | REQUIRED | functions and derived values where publicly exposed
- S07 | REQUIRED | authentication and authorization boundaries
- S08 | REQUIRED | asynchronous loading and event behavior where publicly exposed
- S09 | REQUIRED | OSDK versus Platform API boundary
- S10 | REQUIRED | application-facing interaction boundary

Out of scope unless promoted by an explicit scope change: proprietary source recovery, unsupported claims about hidden storage/scheduling/runtime internals, visual cloning, exhaustive compatibility engineering, and enterprise-scale performance equivalence.

Coverage is always reported as `covered_required / total_required`, with PARTIAL and UNKNOWN listed separately.
