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
| Performance boundary | Live-chain reads account for 98.66%-98.80% of V13 end-to-end latency | V13 chain-read and run-level evidence | SUPPORTED |
| Concurrency effect | Concurrency is the principal observed end-to-end latency factor | V13 factor effects | SUPPORTED |
| Fragmentation | Fragmentation raises local matching cost; end-to-end effect is masked by chain reads | V13 factor effects | SUPPORTED_WITH_LIMITATIONS |
| Locality/cache | Hotspots raise hit rate but caching has no stable end-to-end benefit | V13 cache and paired evidence | SUPPORTED_WITH_LIMITATIONS |
| C(P) advantage | C(P) has no demonstrated Baseline-I-unavailable performance or protocol advantage | V13 paired evidence | REFUTED_AS_ADVANTAGE |
| RC2 interface | The deployed contract, CAP2, gateway, issuer/verifier and PostgreSQL boundary is uniquely frozen | `v13-final/rc2-interface-manifest.json` | SUPPORTED |
| RC2 thesis wording | Chapter 5 reports V13 run-level evidence without using the invalidated run or overstating C(P) | `docs/thesis-drafts/第5章_链上状态驱动的可信授权执行机制_最终定稿.md` | FROZEN |
| Versioned ciphertext and forward revocation | Not implemented or experimentally validated | none | NOT_YET_SUPPORTED |

The earlier 103,680-record performance row is superseded because its collector
protocol materially deviated from the intended request boundary.
