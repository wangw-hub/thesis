# FINAL_P9A_EVIDENCE_FLOW_AUDIT_V1

| Scenario | Classification source | Material source | Final envelope | Strict inputs |
|---|---|---|---|---|
| A1-A4 | `PilotEvidenceClassificationV1` | `MaterialReleaseEvidenceV2` | run-state/material file | structured classification/material + SHA/phase/invariants |
| A5 | same | ordered DENIED→ALLOWED history | same terminal object | history terminal equality |
| A6 | same | DENIED/HEADER_UPDATE_PENDING | same terminal object | valid fail-closed classification |
| A7 | same | guard-produced header-only allowance | four equal projections | conflict rejection |
| A8 | same | ALLOWED | same terminal object | recovery and invariants |

Unclassified field sources: 0. Multiple-authority fields: 0 in the revised code. Runtime confirmation of the new A7 path remains pending.
