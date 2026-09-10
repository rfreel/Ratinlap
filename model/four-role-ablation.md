# Four-role necessity check

Supplement to T008. This resolves the distinction between a smaller number of top-level buckets and preservation of explicit semantic roles.

A representation does not truly ablate a role if it merely renames it as a subtype/tag inside another bucket. The test is: remove the distinction entirely, not just its top-level label.

| Remove role | Attempted merge | REQUIRED distinction lost if not recreated | Result |
|---|---|---|---|
| DEFINITION | merge definitions into undifferentiated STATE/DATA | S01 loses explicit type/instance distinction; S05/S06 lose action/query definition versus invocation/result | NECESSARY ROLE |
| STATE | treat all values as definitions or operation outputs | S02/S03 lose runtime objects/links; S08 loses loading/result/occurrence state | NECESSARY ROLE |
| OPERATION | reify calls as generic records/relations only | S04-S06 lose common invocation/effect distinction across read/compute/validate/write; S08 loses explicit observe/subscribe behavior | NECESSARY ROLE |
| CONSTRAINT | encode validation/auth/cardinality as arbitrary operation code | S05/S07 lose the observable distinction between whether an operation is permitted/valid and what operation it is; access and validation boundaries become implicit | NECESSARY ROLE |

D/L/A uses only three top-level labels, but to satisfy S01-S10 it explicitly reintroduces these roles internally: definition versus instance within DATA, predicates/access rules within LOGIC, and invocation/effect distinctions across LOGIC/ACTION. That is a different grouping, not a successful removal of the distinctions.

Therefore `DEFINITION / STATE / OPERATION / CONSTRAINT` are accepted as four **distinguished semantic roles**, not claims that a storage schema must have four physical node types or that no universal one-record encoding can represent them with tags.
