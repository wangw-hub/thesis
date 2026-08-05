# Chain–Database–Object Reconciliation

- Chain ahead of database: verify receipt, same-block anchor, and objects;
  then CAS the database forward and append recovery audit.
- Database ahead of chain: `CONFLICT`; never auto-anchor.
- Object ahead of chain: orphan or superseded; never current.
- Missing anchored object: restore exact verified bytes from trusted backup,
  otherwise `IRRECOVERABLE_CONTENT_LOSS`.
- Digest conflict: fail closed.
- AuthorizationState ahead of HeaderRegistry: schedule/retain a bounded update
  task; old Header cannot release material in the new context.

The isolated current I6 synthetic anchor intentionally lacks retained object
bytes and is classified irrecoverable rather than silently repaired.
