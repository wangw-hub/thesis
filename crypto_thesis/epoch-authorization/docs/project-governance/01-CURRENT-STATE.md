# Current State

Updated: 2026-07-30

## Git

The V13 final audit uses source HEAD
`26ef5bc8dc7b09e683aae8c7d7012f779f6847ed`. Governance freeze commits add
documentation only; no experiment code, raw data, preregistration, deployed
contract, or chain configuration is changed.

## Research Content 1

Status: `COMPLETED_WITH_SCOPE_ADJUSTMENT`. I* is the semantic and digest
representation. C(P) is a deterministic optional execution IR and ablation
object.

## Research Content 2

Status: `COMPLETED_WITH_VALID_RERUN_EVIDENCE`.

- Infrastructure validation chain: chainId `2026072801`, cold preserved.
- Formal authorization chain: chainId `2026072901`, Besu 26.5.0, four QBFT
  validators and one non-validator RPC.
- Formal Genesis SHA-256:
  `7d431f01aab7d0c55c58c09346ee1f9a43475322a4aca304cfbb172b9b32add4`.
- PostgreSQL 16.14 shared and transaction Nonce tests passed.
- AuthorizationState:
  `0x9ef44cf538d0df457ba77c556d8785e48bfc436d`.
- Contract artifact SHA-256:
  `b8cd8040e4a7683fb4454ea1cf3c3c4d97647611ad7cb3d616b72a35cf496ad5`.
- CAP2 binds chainId, contractAddress, policyDigest, epoch, stateVersion,
  userVersion, userKeyId, operation, validity interval, and Nonce.
- Semantic differences, attack false accepts, duplicate Nonce successes, and
  state-race erroneous issues: 0.
- RPC and PostgreSQL outages fail closed; one-validator recovery passed.

The first 103,680-record formal run is
`INVALIDATED_PROTOCOL_DEVIATION` and cannot support performance claims. The sole
valid run is
`experiments/runs/formal_auth_multihost_rerun_v13_20260729T073007Z_8a3d795/`:
108 factor configurations, 324 seeded configurations, 9,720 run blocks, 77,760
requests, and 233,280 chain reads. Request SHA-256 is
`00dbdc62c21a7c12143394118df5dc00bbe7108d822a4af41bd6a96aa89cc4ce`.

V13 run-level paired analysis finds no stable cache or C(P) engineering
advantage. Live-chain reads account for 98.66%-98.80% of latency.
`C(P)_DEMOTED_CONFIRMED_BY_VALID_RERUN`.

The authoritative RC2 interface is
`docs/reviews/research-content-2/v13-final/rc2-interface-manifest.json`.

The Research Content 2 thesis chapter status is
`CHAPTER_FINALIZED_FROM_VALID_V13_EVIDENCE`. The authoritative chapter is
`docs/thesis-drafts/第5章_链上状态驱动的可信授权执行机制_最终定稿.md`.
It contains eight reproducible V13 data figures, two mechanism diagrams and six
data tables. The thesis wording does not alter the experiment, interface,
contract or formal chain.

## Research Content 3

Status（2026-08-05 同步）：`FORMAL_COMPLETED`（在 `epoch-authorization-r3-prep`
工作树完成：I9 Pilot 93/93、I10 预注册、I11 Formal 145/145 有效、I12-I17 完成）。
本仓库范围至 RC2；RC3 权威入口见根 `docs/project-governance/CURRENT-SNAPSHOT.md`。

## Hard Stops

No active RC2 hard stop. `HS-FUNDING-001` was resolved by the approved separate
formal chain; the old chain was not funded or modified.

## Restrictions

Do not modify V13 raw data or preregistration, do not mix PILOT_ONLY or the
invalidated first run with V13, do not modify the formal chain, do not push, and
do not enter RC3 I0 without the required read-only reconciliation, KeyStore
decision, and explicit approval.
