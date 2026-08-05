# Revision 7 remote preflight

Host `experiment-client` passed the dedicated I9 test suite (41 passed; the
isolated-chain decoder test remained assigned to Bootstrap). A separate real
PostgreSQL check connected only to `127.0.0.1:55432`,
`epoch_auth_r3_i9_pilot`, role `epoch_auth_r3_i9_pilot`, PostgreSQL 16.14.

The simulated Canary name was 44 bytes. `SHOW application_name`,
`current_setting`, and `pg_stat_activity` all matched exactly. Fallback and
port-5432 attempts were zero. Bootstrap then confirmed QBFT chain
2026073005, fixed-block reads, receipt/log reads, CompositeState, and zero
extraData decoding errors.

