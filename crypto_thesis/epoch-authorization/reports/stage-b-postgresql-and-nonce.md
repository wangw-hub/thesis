# Stage B PostgreSQL and Nonce Acceptance

PostgreSQL 16.14 was deployed on `experiment-client` with SCRAM-SHA-256
authentication and a password file restricted outside Git. The service listens
on localhost and the frozen experiment address.

Shared capability nonce results:

| Concurrency | Accepted | Replay rejected | Rows |
|---:|---:|---:|---:|
| 50 | 1 | 49 | 1 |
| 100 | 1 | 99 | 1 |
| 500 | 1 | 499 | 1 |

Transaction nonce reservations were unique for 20/20 and 50/50 concurrent
requests. Reconciliation retained a durable next nonce of 75 when the RPC
pending nonce was 50, so an unknown broadcast nonce was not reused.

Stopping PostgreSQL caused the verifier-side database operation to fail closed.
After restart, all consumed nonce rows remained present. Raw evidence is stored
under `evidence/postgresql/`.
