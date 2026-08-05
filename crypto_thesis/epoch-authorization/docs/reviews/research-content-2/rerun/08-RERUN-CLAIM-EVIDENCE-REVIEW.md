# V13 Claim-Evidence Review

| Claim | Decision | Evidence boundary |
|---|---|---|
| B and C preserve the same I* semantics | `SUPPORTED` | shared workload and prior semantic/attack validation |
| Per-request authorization reads live chain state | `SUPPORTED` | 233,280 trace rows; exactly three reads per request |
| Cache generally improves end-to-end latency | `NOT_SUPPORTED` | both cache comparisons have positive median differences and CIs crossing zero |
| Locality changes cache behavior | `SUPPORTED` | hotspot median hit rates 0.625-0.75; uniform 0.125 |
| C(P) has a unique system advantage | `REFUTED` | no stable paired benefit; higher matcher cost as fragmentation rises |
| Fragmentation affects matcher cost | `SUPPORTED_WITH_LIMITATIONS` | B0 26.0 to 39.7 us; C0 32.5 to 74.7 us; end-to-end effect is masked |
| Concurrency is the dominant measured factor | `SUPPORTED` | median latency rises from about 53 ms to 340-349 ms |
| Live-chain state binding dominates latency | `SUPPORTED` | median chain-read share 98.66%-98.80% |

The defensible Research Content 2 contribution is the auditable integration of
monotonic on-chain state, complete CAP2 binding, shared atomic Nonce control,
multi-verifier consistency, and fail-closed behavior on a real five-node QBFT
network. It is not a claim that C(P) outperforms I*.

