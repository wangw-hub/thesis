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
| D-009 | R2 Stage C | Stop formal role deployment for funding review. | Empty alloc, no funded account, zero validator balances, and nonzero base fee prevented truthful deployment. | Stage-C funding hard-stop evidence. | Resolved by D-011 | SUPERSEDED |
| D-010 | Funding review | Reject in-place QBFT reward transition; recommend separate preallocated formal chain. | Besu transition scope and isolated probe rejected reward transition configuration. | `docs/funding-review/`; preserves present infrastructure chain. | Resolved by D-011 | SUPERSEDED |
| D-011 | R2 formal chain | Approve B1: preserve the old chain and create a separately keyed, preallocated formal authorization chain. | Avoids rewriting accepted infrastructure history while providing auditable test funding. | Formal-chain F0-F13 evidence. | No without architecture review | CURRENT |

Superseded decisions remain recorded rather than deleted. Every future material design decision must add a row here and update the claim and experiment registries.

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

## DEC-R2-CORRECTED-RERUN-V13-20260729

- Status: `CURRENT`
- Decision: accept V13 as the sole formal Research Content 2 performance evidence.
- Reason: all six material collector issues are closed by tests and accepted
  dry-run evidence; the complete rerun passes immutable hash, pairing, trace,
  contamination, and run-level statistical audits.
- Evidence:
  `experiments/runs/formal_auth_multihost_rerun_v13_20260729T073007Z_8a3d795/`
  and `docs/reviews/research-content-2/rerun/09-RERUN-FINAL-DECISION.md`.
- Claim impact: confirms `C(P)_DEMOTED_CONFIRMED_BY_VALID_RERUN`.

## DEC-R2-V13-FINAL-FREEZE-20260730

- Status: `CURRENT`.
- Decision: freeze V13 as the sole formal RC2 performance evidence and freeze
  `rc2-interface-manifest.json` as the unique RC2-to-RC3 interface input.
- Reason: immutable hashes, run-level paired statistics, live-chain bytecode,
  protocol source, and fault/security evidence are mutually consistent.
- Claim impact: RC2 contribution is chain-state anchoring, CAP2 binding, shared
  atomic Nonce, multi-verifier consistency, role governance, and fail-closed
  operation. C(P) remains a derived ablation/falsification IR.
- Interface note: `contracts/interfaces/IAuthorizationState.sol` is a
  `SUPERSEDED_NON_AUTHORITATIVE_STUB`; the deployed ABI and
  `AuthorizationState.sol` are authoritative.

## DEC-R2-CHAPTER-FINAL-20260730

- Status: `CURRENT`.
- Decision: freeze Chapter 5 as
  `CHAPTER_FINALIZED_FROM_VALID_V13_EVIDENCE`.
- Reason: every performance number is traceable to V13 run-level evidence;
  eight data figures and six tables are reproducible; blind review has no FATAL
  or MAJOR issue.
- Claim impact: chain reads are the dominant measured cost, caching has no
  stable engineering benefit, and
  `C(P)_DEMOTED_CONFIRMED_BY_VALID_RERUN` remains final.
- Evidence: `docs/thesis-drafts/research-content-2-final/`.
