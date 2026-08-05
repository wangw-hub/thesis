# Pilot phase contract V1

All runs require `RUN`, `ENVIRONMENT_CHECK`, `RESET`, `WORKLOAD`, and
`EVIDENCE_SEAL`, each with `STARTED` and `COMPLETED`.  Scenario contracts add
actual encryption, object, Header, chain, database, IPFS, fault, or recovery
phases.  Every other known phase is explicitly `NOT_APPLICABLE`.

`NOT_APPLICABLE` is not execution success.  `MISSING` is never converted to a
zero duration.  Sequence, run identity, attempt identity, config digest,
hostname, and monotonic ordering are validated from the append-only JSONL.
