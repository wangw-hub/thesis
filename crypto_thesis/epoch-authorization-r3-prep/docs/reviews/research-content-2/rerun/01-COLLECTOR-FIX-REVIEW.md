# Collector Fix Review

The V2 collector uses request-scoped `BesuStateGateway` traces, distinct frozen
locality sequences, explicit cache lookup results, true batch windows, and
run-level pairing. The invalid predecessor remains unchanged at SHA-256
`64cc50e3a3495e04460040fbf6d9ae8b3459948c3fe2ccd24618f391b47e9e6e`.

Implementation review: `PASS_PENDING_DRY_RUN`. All 97 repository tests pass;
the live trace smoke test returned chainId 2026072901, one request-linked trace,
and non-negative duration. Final issue closure remains conditional on RR10.
