# Recovery Runbook V1

1. Freeze material release and allocate a bounded recovery run ID.
2. Verify KeyStore availability without logging secrets.
3. Verify PostgreSQL connectivity and migration hashes.
4. Verify chainId, contract code, and one same-block dual-contract snapshot.
5. Verify referenced Header and Body objects.
6. Resolve COMMIT_UNKNOWN by hash, then bounded nonce scan; never rebroadcast.
7. Restore exact objects only from trusted immutable backups.
8. Rebuild derived current database/index state only from verified anchors.
9. Append disposition and recovery audit.
10. Run full bounded reconciliation.
11. Enable release only if all selected resources are consistent.
12. Escalate ambiguity, loss, or conflict for manual reconciliation.
