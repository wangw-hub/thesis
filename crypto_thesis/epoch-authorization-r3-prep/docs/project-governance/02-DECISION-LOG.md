# Decision Log

| ID | Stage/date | Decision | Replaced approach and reason | Evidence and impact | Reversible | Status |
| --- | --- | --- | --- | --- | --- | --- |
| D-001 | Thesis reconstruction | Replace self-designed ABE focus with standard components plus verifiable system mechanisms. | Original theoretical closure and implementation risk were insufficient for a master's schedule. | Historical reconstruction report and blueprint; removes unsupported primitive claims. | No without new review | CURRENT |
| D-002 | R1 design | Compile non-continuous policies deterministically into normalized `I*`. | Raw interval input admits order, overlap, duplicate, and split ambiguity. | `time-policy` compiler/tests/E1; supports stable semantics and digest. | No | CURRENT |
| D-003 | R1 E1 review | Make `I*` the semantic primary representation and bind digest to it. | Earlier blueprint bound digest to `C(P)`; execution-format changes should not alter semantic identity. | `time-policy/src/time_policy/serialize.py`, Chapter 4 V1.2. | Only with full revalidation | CURRENT |
| D-004 | R1 E1 review | Demote `C(P)` to optional derived execution IR. | E1 found no stable storage advantage over interval lists and slower Python matching. | E1 formal report; C(P) protocol necessity analysis. | Yes, only with new protocol evidence | CURRENT |
| D-005 | R2 infrastructure | Use real Besu 26.5.0 QBFT with four validators and one non-validator RPC node. | Single-host/Docker substitutes do not satisfy the frozen real consortium-chain requirement. | Multi-host deployment acceptance evidence. | No without architecture review | CURRENT |
| D-006 | R2 protocol | Use CAP2 chain/contract/state/user-version binding. | CAP1 is rejected in chain mode because it lacks formal chain-state binding. | `src/epoch_auth/serialization.py`; CAP2 attack tests. | No without security review | CURRENT |
| D-007 | R2 replay control | Use PostgreSQL atomic shared nonce consumption and transaction nonce reservation. | Per-process nonce state and raw pending-count allocation are insufficient for concurrent services. | Stage B reports and implementations. | No without equivalent audited backend | CURRENT |
| D-008 | Security remediation | Retire a LOCAL_ONLY legacy rpc-1 P2P identity, rewrite local reachable history, and require external secret-file paths. | A tracked historical script contained a real legacy node key. | Security remediation reports, `prepare.ps1`, commits listed in source index. | Archive retained; active identity cannot be restored | CURRENT |
| D-009 | R2 Stage C | Stop formal role deployment for funding review. | Empty alloc, no funded account, zero validator balances, and nonzero base fee prevent truthful deployment. | Stage-C funding hard-stop evidence. | Yes after approved funding solution | CURRENT_HARD_STOP |
| D-010 | Funding review | Reject in-place QBFT reward transition; recommend separate preallocated formal chain. | Besu transition scope and isolated probe reject reward transition configuration. | `docs/funding-review/`; preserves present infrastructure chain. | Requires explicit user approval | HARD_STOP_AWAITING_USER_DECISION |

Superseded decisions remain recorded rather than deleted. Every future material design decision must add a row here and update the claim and experiment registries.

## DEC-R3-I10-20260802

- Status: `CURRENT_DESIGN_ONLY`.
- Decision: freeze six formal RQs, seven claim records (one explicit forbidden
  QBFT claim), eight factor records, twelve metrics, RUN-level analysis,
  blocked deterministic order, matched Local/Kubo recovery blocks, and a
  180-run minimum-sufficient budget under `I10_COMPLETED_AWAITING_I11_APPROVAL`.
- Boundaries: HEADER_ONLY and BODY_ROTATION remain separate semantic classes;
  I9 Pilot timing is forbidden as formal performance evidence; RC2 and RC3
  formal assets are disjoint; no multi-node RC3 Formal deployment is admitted.
- Evidence: `docs/research-content-3-implementation/i10/` and its artifact
  manifest. No Formal attempt or data was created.

## DEC-R3-P9A-EVIDENCE-CONTRACT-20260801

- Status: `CURRENT_REQUIRES_RUNTIME_EVIDENCE`.
- Decision: retain the smoke-label requirement, introduce structured classification and material-release evidence, and allow `P9_A_PASSED` only from strict `P9AAcceptanceDecisionV1`.
- Boundary: no business protocol, contract, ABI, revocation, recovery, or frozen raw modification.
- Pending: explicitly authorized A7-only real-chain development evidence.
- Evidence: `docs/research-content-3-implementation/i9-p9a-evidence-final/`.

## DEC-B1-20260729

- Status: `CURRENT`
- Decision: preserve chain 2026072801 as `INFRASTRUCTURE_VALIDATION_CHAIN`; use independent chain 2026072901 as `FORMAL_AUTHORIZATION_EXPERIMENT_CHAIN`.
- Reason: resolve empty-alloc funding without rewriting accepted chain history.
- Result: formal-chain F0-F12 validated; BOOTSTRAP_FUNDER has no business role.
- Evidence: `infra\besu-qbft-multihost\formal-authorization-chain\evidence\f12\formal-experiment-admission.json`.

## DEC-R2-FORMAL-20260729

Formal evidence confirms `C(P)_DEMOTED_CONFIRMED`; Research Content 2 contribution centers on chain binding, shared Nonce, multi-verifier consistency and fail-closed execution.

## DEC-R2-STRICT-REVIEW-20260729

- Status: `CURRENT`
- Decision: supersede the first formal performance conclusions and require a full rerun.
- Reason: material deviations in live-chain access, locality generation, throughput,
  cache-hit measurement, and statistical unit handling.
- Evidence: `docs/reviews/research-content-2/01-PREREGISTRATION-COMPLIANCE-AUDIT.md`.
