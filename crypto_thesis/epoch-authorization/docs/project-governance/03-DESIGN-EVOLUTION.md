# Design Evolution

1. **Original proposal (HISTORICAL_ONLY):** pursued a broad time-constrained blockchain sharing design with custom cryptographic ambitions. Strict review found theoretical and engineering closure risks.
2. **System reconstruction and Blueprint V1.0 (PARTIALLY_VALID):** preserved the thesis topic and three-step progression while adopting standard cryptographic components, policy compilation, chain state, and reproducible experiments. The old digest-to-`C(P)` detail is superseded.
3. **R1 implementation and E1 (CURRENT):** raw time policies are normalized into `I*`; canonical serialization and `policyDigest` bind semantic intervals and time interpretation. `C(P)` is generated separately.
4. **R1 scope adjustment (CURRENT):** formal evidence showed `C(P)` has no general interval-list storage advantage and slower Python matching. It became an optional execution IR and falsification object, not the primary claimed advantage.
5. **R2 local authorization prototypes (CURRENT, pre-formal-chain):** Baseline-I/Baseline-I-Cache and Proposed-C/Proposed-C-Cache were implemented with CAP2 tests and fair-comparison rules.
6. **Five-host Besu QBFT (CURRENT):** a real four-validator plus one RPC-node environment was installed, validated, restarted, and security-remediated without changing its frozen Genesis.
7. **Security remediation and PostgreSQL nonce backend (CURRENT):** a legacy local-only rpc-1 identity was retired; reachable local Git history was sanitized; shared replay and transaction nonce controls were validated on PostgreSQL.
8. **Funding hard stop (SUPERSEDED):** the original frozen chain had no fundable sender. The stop was resolved without modifying that chain by approving an independent formal authorization chain.
9. **Formal authorization chain (CURRENT):** B1 created a separately keyed, preallocated chain for formal roles, AuthorizationState, CAP2, security tests, controlled faults, PILOT_ONLY, and formal performance evidence.
10. **First formal run (HISTORICAL_ONLY):** 103,680 records were retained but invalidated because the collector materially deviated from the intended live-chain, locality, cache, throughput, and statistical boundaries.
11. **Corrected V13 rerun (CURRENT):** a new preregistration and complete 77,760-request run restored three per-request live reads, valid locality/cache/throughput measurement, complete pairings, and run-level bootstrap inference.
12. **RC2 final freeze (CURRENT):** V13 confirms chain-read dominance and no stable cache or C(P) engineering advantage. RC2 closes around state binding, shared Nonce, multi-verifier consistency, and fail-closed behavior.

The final thesis storyline is therefore not a cosmetic repair: R1 establishes
semantic determinism and boundaries; R2 establishes real authorization-state
execution and its measured limits; R3 remains an independently gated next
stage. Earlier ideas remain available for historical audit but cannot override
current evidence.

## Independent formal authorization chain

The empty-alloc infrastructure chain remains preserved. A separately keyed and preallocated B1 chain now carries formal roles, AuthorizationState, CAP2 integration, security tests, controlled faults and PILOT_ONLY validation.

## Formal Research Content 2 evidence

The 103,680-record first run does not support formal conclusions. The corrected
V13 run contains 9,720 run blocks, 77,760 requests, and 233,280 chain reads and
confirms `C(P)_DEMOTED_CONFIRMED_BY_VALID_RERUN`.
