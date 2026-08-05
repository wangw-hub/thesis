# V13 Run-Level Statistical Review

## Unit Of Inference

The primary unit is `workload_id x seed x repetition`. Request rows are used
only for within-run summaries and integrity checks. All four methods are paired
on 2,430 complete run units. This avoids request-level pseudoreplication.

## Confirmatory Comparisons

| Comparison | Mean difference | Median difference | 95% bootstrap CI for mean | Interpretation |
|---|---:|---:|---:|---|
| B1-B0 | +1.688 ms | +0.390 ms | [-0.220, +3.539] ms | no reliable cache benefit |
| C1-C0 | +1.419 ms | +0.176 ms | [-0.410, +3.258] ms | no reliable cache benefit |
| C0-B0 | +1.315 ms | +0.257 ms | [-0.568, +3.177] ms | no reliable C(P) benefit |
| C1-B1 | +1.046 ms | +0.408 ms | [-0.717, +2.886] ms | no reliable C(P) benefit |

The bootstrap used 10,000 resamples with seed `2026072913`. Differences are
left-minus-right; therefore positive values denote higher latency. Robust
effects were between 0.008 and 0.019 in absolute value. Direction was unstable:
each comparison improved in roughly 44% of runs and degraded in roughly 47%.

## Engineering Significance

The paired intervals span zero and the direction varies across runs. Matcher
differences are orders of magnitude below common live-chain read time. Neither
cache use nor C(P) demonstrates a stable engineering advantage under the
pre-registered full protocol.

