# Metric Definition Review

Durations use `perf_counter_ns`; chain read traces are measured at the gateway;
throughput uses completed/successful counts divided by the observed batch
window. Request and run schemas preserve the natural paired structure. Verdict:
`PASS_PENDING_DRY_RUN`.
