# Object Backup and Restore

Backups are test-only immutable files outside the repository. Restoration
requires the exact expected SHA-256 and size, publishes through
`LocalObjectStore.put`, and verifies the final object before success. A missing
or corrupt backup is fail-closed. A chain digest is evidence, not a backup.
