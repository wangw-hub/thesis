# Revision Canary result

## Attempt 1

`I9_REVISION_1_20260730T131319Z_ca0a002` failed before workload entry with
`MODULE_IMPORT_ROOT_MISSING`.  P9-A was not scheduled.  The failed attempt was
sealed read-only and excluded from all later processing.

## Attempt 2

`I9_REVISION_2_20260730T131942Z_105b4c0` executed on `experiment-client`
from the committed remote snapshot.  It reached the isolated chain and created
the Canary-only resource and Anchor.  During the subsequent composite read,
the runner compared tuple index 1 (`resourceId: bytes32`) with integer 1 rather
than reading index 5 (`headerVersion`) and index 15 (`exists`).  Python raised
`TypeError` before evidence sealing.

The append-only remote phase journal is retained under the attempt runtime
root.  The run is `INVALID_CANARY_COMPONENT_ASSERTION`; it is not a valid
Pilot run, is not silently retried, and is excluded from pairing and
statistics.  P9-A, P9-B, P9-C, and P9-D were not scheduled.

The tuple assertion is corrected in the local worktree, but the correction has
not been executed.  A new committed snapshot and a new attemptId require
explicit follow-up approval.
