# Failure and Fix Log

| ID | Class | Root cause | Regression | Status |
| --- | --- | --- | --- | --- |
| FIX_001 | RUNNER_DEFECT | development matrix duplicated business paths | shared `execute_one` path tests | VERIFIED |
| FIX_002 | DEPLOYMENT_DEFECT | no atomic full-development bootstrap | bootstrap atomicity test | VERIFIED |
| FIX_003 | DEPLOYMENT_DEFECT | historical password filename contained a trailing CR | normalized external 0600 runtime file | VERIFIED |
| FIX_004 | TEST_DEFECT | fault runner referenced nonexistent `JOB_CREATE` role | frozen-role assertion | VERIFIED |
| FIX_005 | DEPLOYMENT_DEFECT | old development identities under `autonomous/*/raw` were not scanned | nested identity bootstrap test | VERIFIED |

All changes preserve the frozen protocol/ABI. Security or scientific standards were not weakened.
