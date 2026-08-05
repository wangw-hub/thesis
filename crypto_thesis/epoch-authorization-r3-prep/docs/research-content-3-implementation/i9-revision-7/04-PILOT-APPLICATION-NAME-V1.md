# PilotApplicationNameV1

`PilotApplicationNameV1` emits `r3i9-<role>-<digest>` using only lowercase
ASCII letters, digits, and hyphens. The digest is the first 32 hexadecimal
characters of SHA-256 over the domain
`EPOCH_AUTH_R3_I9_PG_APPLICATION_NAME_V1`, attempt ID, run identity, frozen
role, and software commit with unambiguous NUL separators.

The full attempt ID and run ID affect the digest but never appear in the
name. Maximum output length is below the frozen 63-byte limit. The finite roles
are bootstrap, canary, migration, fixture, job, worker, evidence, quality,
snapshot, and finalize. Unknown or free-text roles are rejected.

