# Recovery Snapshot V1

`RecoverySnapshotV1` records chain ID, one block number/hash, both contract
states, the PostgreSQL transaction view, workflow rows, attempts, events,
object references and verification results, CK status, recipient-index status,
and cursor state. `capturedAt` is audit metadata and is excluded from the
deterministic snapshot digest.

The snapshot never claims global atomicity between blockchain, database, file
system, and KeyStore.
