# V13 Corrected Rerun Result Peer Review

## Verdict

`ACCEPT_WITH_LIMITATIONS`. The corrected run satisfies the frozen protocol and
completeness requirements. It contains 9,720 paired run blocks, 77,760 request
records, and 233,280 independently recorded live-chain reads. Every request has
exactly three reads, and no failed request, missing pairing, duplicate key,
PILOT_ONLY row, invalidated-run row, chain mismatch, or contract mismatch was
observed.

## Performance

Run-level median end-to-end latency was 196.128 ms (B0), 196.583 ms (B1),
198.682 ms (C0), and 198.939 ms (C1). The paired mean differences all had 95%
bootstrap intervals spanning zero. Cache variants did not provide a stable
engineering benefit: B1-B0 had a median difference of +0.390 ms, while C1-C0
had +0.176 ms. Positive values mean that the cache variant was slower.

Concurrency dominated latency: method medians rose from about 52.8 ms at
concurrency 1 to 196-199 ms at concurrency 4 and 340-349 ms at concurrency 16.
Throughput remained near 17.7-18.0 requests/s, indicating serialization or
capacity saturation in the common live-chain read path.

## Method Boundary

Policy matching occupied tens of microseconds, while live-chain reads accounted
for 98.66%-98.80% of median end-to-end latency. Fragmentation increased matcher
cost, especially for C(P), but this effect was masked at the end-to-end level.
Hotspot locality increased cache hit rates, but the additional cache path did
not translate into a reliable latency reduction.

## Claim Decision

`C(P)_DEMOTED_CONFIRMED_BY_VALID_RERUN`. C(P) remains a deterministic derived
execution IR and ablation object. The corrected evidence does not establish an
advantage that the I* baseline cannot reproduce.

