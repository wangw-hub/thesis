# I7 Recovery Scenario Matrix

| ID | Scenario | Expected outcome | Result |
|---|---|---|---|
| R1 | Consistent state | release allowed | PASS |
| R2 | Chain confirmed, DB interrupted | verify then CAS DB | PASS |
| R3 | DB prematurely COMMITTED | conflict/manual | PASS |
| R4 | Header stored, worker crashed | orphan/retry | PASS |
| R5 | New Body, no Header | orphan | PASS |
| R6 | RPC disconnect, known tx hash | receipt recovery, no rebroadcast | PASS |
| R7 | Unknown hash, known nonce | bounded unique match | PASS |
| R8 | Isolated Besu stop/recover | fail closed then recover | PASS |
| R9 | Isolated PostgreSQL stop/recover | fail closed then recover | PASS |
| R10 | Scanner stop | cursor-based idempotent resume | PASS |
| R11 | Header missing, trusted backup | exact restore | PASS |
| R12 | Header missing, no backup | irrecoverable content loss | PASS |
| R13 | Body corrupt | digest failure | PASS |
| R14 | ROOT_KEK transiently unavailable | fail closed | PASS |
| R15 | ROOT_KEK permanently lost | irrecoverable key loss | PASS |
| R16 | Database backup restore | independent restore, 11/11 migrations | PASS |
| R17 | Recipient index lost | rebuild from verified current Header | PASS |
| R18 | Old task superseded | superseded, no commit | PASS |
| R19 | Anchor/object digest conflict | conflict, fail closed | PASS |
| R20 | Anchor exists, DB records lost | derived current state, incomplete history | PASS |

“PASS” means the expected safe disposition was observed; it does not mean the
fault disappeared or that lost content/key material was recovered.
