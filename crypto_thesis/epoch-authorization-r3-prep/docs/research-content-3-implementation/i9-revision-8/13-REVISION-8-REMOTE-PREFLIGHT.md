# Revision 8 Remote Preflight

Host: `experiment-client`. PostgreSQL 16.14 at `127.0.0.1:55432`; database and application-name attestation passed.

The real PostgreSQL gate proved explicit `JOB_CREATE` commit, visibility from an independent connection, rollback invisibility, two-transaction plan freeze, admission, and zero preflight chain writes. Exact administrator cleanup removed only named preflight rows.

The final remote suite passed 46/46, including a read-only CompositeState query through the QBFT-compatible Web3 factory. New port-5432 attempts: 0; Web3 factory bypasses: 0; `ExtraDataLengthError`: 0.
