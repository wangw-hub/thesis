# I7 Invariant Report

All 20 recovery invariants passed:

1. Each field has one authority.
2. Header self-claims never establish current state.
3. Same-block dual-contract reads are explicit.
4. PostgreSQL snapshots are transaction-scoped.
5. Material release starts disabled.
6. Only fully consistent resources permit release.
7. Chain-ahead recovery verifies receipt and objects.
8. Database-ahead state never auto-anchors.
9. COMMIT_UNKNOWN never re-broadcasts.
10. Known-nonce scans are finite and unique-match only.
11. Missing anchored objects require exact trusted backup.
12. Corrupt objects never return bytes as success.
13. ROOT_KEK unavailability fails closed.
14. Permanent key loss is not disguised as retryable.
15. Derived state is explicitly labelled and history-incomplete.
16. Recipient index is rebuilt only from anchored verified Header bytes.
17. Scanner resume preserves cursor continuity.
18. Stale workers cannot commit.
19. Recovery audit rows are append-only.
20. Every repair is followed by reconciliation.

Observed invariant violations: **0**.
