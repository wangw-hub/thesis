# Pilot attempt identity V1

`R3PilotAttemptIdentityV1` binds the attempt purpose, immutable parent
`INVALIDATED_I9_ATTEMPT_0`, repair commit, environment digest, creation time,
and status.

`configDigest = SHA-256(EPOCH_AUTH_R3_I9_PILOT_CONFIG_V1 || canonical config)`.

`runId = SHA-256(EPOCH_AUTH_R3_I9_PILOT_RUN_ATTEMPT_V1 || attemptId ||
configDigest || executionAttemptOrdinal)`.

The ordinal is frozen to zero for this attempt.  A rerun requires a new ordinal
or a new attempt; this revision chooses a new attempt rather than overwriting.
