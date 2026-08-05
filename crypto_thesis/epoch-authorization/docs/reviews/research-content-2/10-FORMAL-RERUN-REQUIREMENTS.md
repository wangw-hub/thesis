# Formal Rerun Requirements

1. Read live authorization state through `BesuStateGateway` at the preregistered
   request boundary and record each actual chain read.
2. Implement and unit-test all three locality generators.
3. Measure throughput from batch start/end and completed request count.
4. Record per-request cache hit without cumulative inference.
5. Do not execute an untimed matcher call that warms the measured cache.
6. Preserve pairing keys for method, workload, seed, repetition, and request.
7. Use run-level paired bootstrap as the primary inferential unit.
8. Add automated tests proving metric definitions before a new preregistration commit.
9. Run a new dry-run with a separate Nonce namespace.
10. Store the rerun under a new directory; never overwrite the invalidated raw data.
