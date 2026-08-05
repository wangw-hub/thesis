# Service Recovery Order

1. Restore external KeyStore availability.
2. Restore isolated PostgreSQL and verify migrations/invariants.
3. Restore isolated Besu and verify chain ID, contracts, and block context.
4. Verify immutable objects/backups.
5. Resume scanner, then workers.
6. Run bounded full reconciliation.
7. Enable material release only after consistency.

The exercise stopped only PostgreSQL `16/r3_i4` and
`epoch-auth-r3-i5-besu.service`. PostgreSQL `16/main` retained PID `52520`,
its 2026-07-29 start time, and both frozen configuration hashes.
