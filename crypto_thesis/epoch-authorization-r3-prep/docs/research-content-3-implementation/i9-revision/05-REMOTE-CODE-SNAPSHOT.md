# Remote code snapshot

## Superseded Canary snapshot

Repair commit `ca0a0027d8bad1e9083db242f654379c46a3e5c3` was archived as
`f0214e4973387273ec5fadfe1e71105f5d111bb15fc2bfd34fe2cd578f7b3259`.
The remote SHA matched exactly.  Attempt
`I9_REVISION_1_20260730T131319Z_ca0a002` failed before workload entry because
the archive runner inserted `src/` but not the repository root into
`sys.path`, so importing the committed `scripts.r3_i5` helper failed.

No Pilot run directory, chain transaction, database mutation, or P9-A task was
created.  The attempt is retained as `CANARY_IMPORT_ROOT_FAILED` and excluded
from all statistics.  It is not retried or overwritten.

## Corrective rule

The next snapshot must include both the immutable repository root and `src/`
in the module search path, pass the same local tests, receive a new commit SHA,
archive SHA, and attemptId, and restart at a single Canary.
