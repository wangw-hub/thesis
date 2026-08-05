# Proposed Governance Updates After I7

- Record I7 as `I7_COMPLETED_AWAITING_I8_APPROVAL`.
- Freeze RecoveryAuthorityMatrixV1, RecoveryDispositionV1, and the bounded
  RecoveryCoordinator.
- Preserve Bonsai historic-state and synthetic-object-retention limitations.
- Record that COMMIT_UNKNOWN recovery never re-broadcasts.
- Record the independent PostgreSQL restore evidence and unchanged formal
  database/chain boundary.
- Do not start I8 without explicit approval.
