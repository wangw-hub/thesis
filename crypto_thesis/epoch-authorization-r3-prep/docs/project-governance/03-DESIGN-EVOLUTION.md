# Design Evolution

1. **Original proposal (HISTORICAL_ONLY):** pursued a broad time-constrained blockchain sharing design with custom cryptographic ambitions. Strict review found theoretical and engineering closure risks.
2. **System reconstruction and Blueprint V1.0 (PARTIALLY_VALID):** preserved the thesis topic and three-step progression while adopting standard cryptographic components, policy compilation, chain state, and reproducible experiments. The old digest-to-`C(P)` detail is superseded.
3. **R1 implementation and E1 (CURRENT):** raw time policies are normalized into `I*`; canonical serialization and `policyDigest` bind semantic intervals and time interpretation. `C(P)` is generated separately.
4. **R1 scope adjustment (CURRENT):** formal evidence showed `C(P)` has no general interval-list storage advantage and slower Python matching. It became an optional execution IR and falsification object, not the primary claimed advantage.
5. **R2 local authorization prototypes (CURRENT, pre-formal-chain):** Baseline-I/Baseline-I-Cache and Proposed-C/Proposed-C-Cache were implemented with CAP2 tests and fair-comparison rules.
6. **Five-host Besu QBFT (CURRENT):** a real four-validator plus one RPC-node environment was installed, validated, restarted, and security-remediated without changing its frozen Genesis.
7. **Security remediation and PostgreSQL nonce backend (CURRENT):** a legacy local-only rpc-1 identity was retired; reachable local Git history was sanitized; shared replay and transaction nonce controls were validated on PostgreSQL.
8. **Funding hard stop (CURRENT):** formal roles and AuthorizationState deployment cannot proceed honestly because the frozen chain has no fundable sender. No later R2 result may be claimed until this is resolved by an approved, evidence-preserving path.

The final thesis storyline is therefore not a cosmetic repair: R1 establishes semantic determinism and boundaries; R2 must establish real authorization-state execution; R3 remains future work. Earlier ideas remain available for historical audit but cannot override current evidence.

## Independent formal authorization chain

The empty-alloc infrastructure chain remains preserved. A separately keyed and preallocated B1 chain now carries formal roles, AuthorizationState, CAP2 integration, security tests, controlled faults and PILOT_ONLY validation.

## Formal Research Content 2 evidence

The preregistered 103,680-record formal run confirms the system contribution while retaining `C(P)_DEMOTED_CONFIRMED`.
