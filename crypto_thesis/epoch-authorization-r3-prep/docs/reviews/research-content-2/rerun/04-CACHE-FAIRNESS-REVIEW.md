# Cache Fairness Review

B1 and C1 share capacity 256, TTL 60 seconds, and LRU semantics. Each lookup
returns its own hit result; B0/C0 do not instantiate a cache. V2 uses
`COLD_START_PER_REPETITION`; warmups use disposable executors and cannot warm a
measured cache. Entry-count fairness is primary; byte-size differences remain a
declared representation limitation. Verdict: `PASS_PENDING_DRY_RUN`.
