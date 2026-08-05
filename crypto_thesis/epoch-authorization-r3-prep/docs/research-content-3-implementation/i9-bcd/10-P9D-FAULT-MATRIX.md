# P9-D Frozen Fault Matrix

The twelve scenarios are SCANNER_RESTART, LEASE_EXPIRED, POST_CHAIN_DB_FAILURE,
COMMIT_UNKNOWN, POSTGRES_UNAVAILABLE, BESU_UNAVAILABLE, KUBO_UNAVAILABLE,
RELEASE_WINDOW, SUPERSEDED_EVENT, INCOMPLETE_INDEX, ROOT_KEK_UNAVAILABLE, and
NO_REPLICA. Each uses seeds 401 and 402, for 24 total runs. Each final run must
include independent `FaultInjectionEvidenceV1` injection and observation
evidence; an expected fail-closed outcome is still a valid Pilot sample.
