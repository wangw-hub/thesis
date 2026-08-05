# V13 Statistical Claim Review

Status: `VALIDATED_WITH_LIMITATIONS`

## Confirmatory estimates

The statistical unit is one
`fragmentation × locality × concurrency × seed × repetition × method` run.
Comparisons are naturally paired by workload, seed, and repetition. Request
records describe within-run distributions but are not treated as independent
replicates.

| Method | Run-level median end-to-end latency |
|---|---:|
| B0 | 196.128 ms |
| B1 | 196.583 ms |
| C0 | 198.682 ms |
| C1 | 198.939 ms |

| Paired contrast | Median difference | Mean difference | 95% bootstrap CI for mean |
|---|---:|---:|---:|
| B1 - B0 | +0.390 ms | +1.688 ms | [-0.220, +3.539] ms |
| C1 - C0 | +0.176 ms | +1.419 ms | [-0.410, +3.258] ms |
| C0 - B0 | +0.257 ms | +1.315 ms | [-0.568, +3.177] ms |
| C1 - B1 | +0.408 ms | +1.046 ms | [-0.717, +2.886] ms |

Each contrast contains 2,430 paired runs. Bootstrap resampling is performed at
run level with 10,000 resamples and seed `2026072913`. Confidence intervals
cross zero. Improvement proportions are about 43.7%-44.3%, degradation
proportions about 46.6%-47.4%, and the remainder is within the preregistered
1 ms no-material-change band. Directions vary across seeds and factors.

## Factor review

- `SUPPORTED`: concurrency is the dominant observed factor. Median end-to-end
  latency rises from roughly 52.8 ms at concurrency 1 to 196-199 ms at 4 and
  340-349 ms at 16.
- `SUPPORTED_WITH_LIMITATIONS`: fragmentation increases local match cost. For
  example B0 rises from about 26.0 us to 39.7 us and C0 from about 32.5 us to
  74.7 us, but this is masked at end-to-end scale.
- `SUPPORTED_WITH_LIMITATIONS`: hotspots increase cache-hit rate; uniform
  requests yield much lower hit rates. Higher hit rate does not translate into
  a stable end-to-end reduction.
- `NOT_SUPPORTED`: B1 or C1 provides a stable engineering-significant cache
  benefit under the tested system boundary.
- `NOT_SUPPORTED`: C(P) provides an advantage that the I* baseline cannot
  reproduce.

## Cost composition

Live chain reads account for 98.66%-98.80% of end-to-end latency. Local matching
accounts for about 0.017%-0.047%. The public chain-read and cryptographic path
therefore dominates small representation-level differences.

Median batch throughput is about 17.78-17.93 requests/s and does not establish a
method-specific advantage. Recorded memory is essentially unchanged across
methods. The stored CPU field is a cumulative process-time counter rather than
a utilization sample, so it cannot support a CPU-efficiency claim.

## Frozen conclusion

`C(P)_DEMOTED_CONFIRMED_BY_VALID_RERUN`.

C(P) remains a deterministic derived execution IR useful for ablation and
falsification. The V13 evidence does not support presenting it as a core
performance or protocol contribution.
