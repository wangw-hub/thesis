# Strict acceptance requirements matrix

| Requirement | Producer | Serialized field | Validator/decision | Test |
|---|---|---|---|---|
| planned/actual/valid=8 | runner result set | decision counts | Acceptance V1 | count and dry-run tests |
| classification=0 | classification factory | evidenceClassification/labels | run validator | propagation/missing-label tests |
| phase errors=0 | phase journal | phase events/result | phase validator/Acceptance | existing phase tests |
| raw SHA=0 | evidence writer | artifact-sha256 | raw validator | existing evidence tests |
| mirror SHA=0 | mirror/archive verifier | acceptance input | Acceptance V1 | decision tests |
| DB invariant=0 | DB evidence producer | invariantViolations | Acceptance V1 | existing DB evidence tests |
| chain invariant=0 | chain evidence producer | invariantViolations | Acceptance V1 | existing chain tests |
| material errors=0 | Material V2 | current/history/projections | run validator | material conflict tests |
| duplicates=0 | DB/chain evidence | duplicate counts | Acceptance V1 | existing + decision tests |
| TRUE_SECRET=0 | secret scan | acceptance input | Acceptance V1 | decision/scan |
| UNCLASSIFIED=0 | data-quality scan | acceptance input | Acceptance V1 | decision/scan |
| formal mix=0 | classification scan | acceptance input | Acceptance V1 | classification tests |
| FATAL=0 | strict review | acceptance input | Acceptance V1 | decision tests |
| MAJOR=0 | strict review | acceptance input | Acceptance V1 | major-blocks-gate test |
| material decision/count consistency | terminalizer | gate decision | CAS terminalizer | gate tests |
| local/remote same decision | acceptance serializer | acceptanceDecision | readback | round-trip test |

Requirement count: 16. Missing producers: 0.
