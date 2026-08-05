# BCDProtocolFreezeDigest

`BCDProtocolFreezeDigest` is reconstructed from the current frozen source
matrix in `scripts/r3_i9/run_revised_remote_pilot.py`, the I9 design records
`13`--`19`, and the post-P9-A stabilization evidence.  The matrix is therefore
not redesigned during execution.

| Stage | Frozen matrix | Seeds | Runs | Statistical unit |
| --- | --- | --- | ---: | --- |
| P9-B | HEADER_ONLY: recipients {2,8,32} x affected {1,4}; BODY_ROTATION: body bytes {65536,1048576,8388608} x recipients {2,8,32} | 101--103; 201--203 | 45 | RUN |
| P9-C | LOCAL_READ, LOCAL_IPFS, HEADER_RESTORE, BODY_RESTORE, CORRUPT_RESTORE, KUBO_UNAVAILABLE, CID_MISMATCH, BOTH_MISSING | 301,302 | 16 | RUN |
| P9-D | SCANNER_RESTART, LEASE_EXPIRED, POST_CHAIN_DB_FAILURE, COMMIT_UNKNOWN, POSTGRES_UNAVAILABLE, BESU_UNAVAILABLE, KUBO_UNAVAILABLE, RELEASE_WINDOW, SUPERSEDED_EVENT, INCOMPLETE_INDEX, ROOT_KEK_UNAVAILABLE, NO_REPLICA | 401,402 | 24 | RUN |

All stages use the existing Pilot endpoint, chain id, contracts, Kubo endpoint,
and PostgreSQL 55432 identity.  The phase contract remains
`contract_for(scenario)` and every timing record is
`PILOT_TIMING_DIAGNOSTIC_ONLY`; HEADER_ONLY and BODY_ROTATION are not a
cross-semantic performance comparison.

Digest algorithm: SHA-256 of the canonical JSON representation of this table
and the named source paths, recorded when the first executable BCD commit is
created.
