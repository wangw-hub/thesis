# Claim-Evidence Matrix

| Claim | Allowed statement | Evidence | Status |
|---|---|---|---|
| Deterministic policy semantics | `I*` provides the canonical semantic and digest input | Research Content 1 tests and E1 records | SUPPORTED |
| Hierarchical cover | `C(P)` is an optional deterministic execution IR, not a universal compression win | E1 formal report | SUPPORTED_WITH_LIMITATION |
| Five-node QBFT | A real four-validator plus one RPC Besu 26.5.0 chain was validated | formal-chain F5 evidence | SUPPORTED |
| Authorization state | AuthorizationState roles and irreversible revocation passed live-chain tests | F7 deployment and state-machine evidence | SUPPORTED |
| CAP2 binding | CAP2 binds chain, contract, stateVersion and userVersion; digest binds `I*` | F8 evidence | SUPPORTED |
| B/C semantics | 1,000 sampled requests had zero unexplained decision differences | F9 evidence | SUPPORTED_FOR_TESTED_INPUTS |
| Replay protection | Shared PostgreSQL Nonce allowed one success at 50/100/500 concurrency | Stage B and F9 evidence | SUPPORTED |
| Fault behavior | RPC and PostgreSQL outages fail closed; one validator can recover | F10 evidence | SUPPORTED |
| Performance | PILOT_ONLY validates collection only and is not formal performance evidence | F11 raw audit | NOT_YET_FORMAL |
| Formal R2 performance | 103,680 preregistered records support system boundaries; no unique C(P) advantage | formal_auth_multihost_20260729_34af4ff | SUPPORTED |
| R3 formal correctness/security/recovery claims | Supported by the frozen I10 claim matrix and RUN-level formal evidence | `docs/research-content-3-implementation/i10/formal-claim-matrix.json` + `docs/research-content-3-implementation/i11/` + `experiments/r3/formal/raw` | SUPPORTED_BY_FORMAL_EXPERIMENT (145/145 valid RUNs; wrong material release 0; state consistency 0) |
| R3 QBFT consensus performance | Explicitly forbidden; no single-node or Pilot observation may support it | `docs/research-content-3-implementation/i10/18-RC3-MULTINODE-DECISION.md` | FORBIDDEN |

> Updated 2026-08-05：早期“RC3 版本化密文与前瞻撤销未实现/未验证”行已被 I11 正式实验支持，
> 标记为 **SUPERSEDED**（历史事实，不删除）。R3 正式结论以
> `i12/05-CLAIM-EVIDENCE-MATRIX.md`（C-01..C-06 SUPPORTED，C-07 FORBIDDEN）为准。
