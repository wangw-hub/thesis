# PilotJobVisibilityGateV1

After the create connection is released, a new independently attested connection must observe the exact run, attempt, resource, operation, update kind, Header and Body digests, object digests, and `READY_FOR_CHAIN_SUBMISSION` state.

Missing rows produce `JOB_LOOKUP_NOT_FOUND`; mismatches produce `JOB_STATE_CONFLICT`. Neither is a database-identity error.
