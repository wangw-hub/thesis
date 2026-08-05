# V13 Final Evidence Audit

Status: `VALIDATED`

Audited source Git HEAD: `26ef5bc8dc7b09e683aae8c7d7012f779f6847ed`
Audit date: 2026-07-30

## Scope

This is a read-only terminal audit of the V13 rerun. No experiment, raw record,
preregistration artifact, deployed contract, or chain configuration was changed.
The first formal run remains `INVALIDATED_PROTOCOL_DEVIATION` and is retained
only for audit.

## Immutable evidence

| Item | Recalculated result |
|---|---|
| V13 preregistration commit | `8a3d795e22e5d9373c3053245e3b4040cd062dd5` |
| V13 experiment-code commit | `8a3d795e22e5d9373c3053245e3b4040cd062dd5` |
| Preregistration artifact index | `00d7f018bf19fb337e8853c421847adbe69b0fbf363ebc83f35478252ae85941` |
| Raw artifact index | `3cb273c3d1938fb4af2dee4d9f0c78f69033380efd0c37f68ae3258990720680` |
| Request records | `00dbdc62c21a7c12143394118df5dc00bbe7108d822a4af41bd6a96aa89cc4ce` |
| Chain-read records | `3e7f5c4948ea66819c68b117b4ca7eaeddfc589e4e3bc52e56b0608ec473ff9b` |
| Batch records | `c99c410f4d6d3c015e806355049dbb4d03e77f011f76a00ca1c5915a0f851b16` |
| Run-level metrics | `175f6a2f0805d07ede897eb3875e1a167b07c4c6050a0d9084e490da0567c760` |
| Invalidated first-run raw data | `64cc50e3a3495e04460040fbf6d9ae8b3459948c3fe2ccd24618f391b47e9e6e` |

All recalculated values match the frozen manifests. The V13 run contains 108
factor configurations, 324 seeded configurations, 9,720 run blocks, 77,760
request records, and 233,280 chain-read records.

## Integrity checks

- Missing pairings: 0.
- Duplicate records: 0.
- `PILOT_ONLY` contamination: 0.
- Invalidated-run contamination: 0.
- Semantic differences: 0.
- Attack false accepts: 0.
- duplicate Nonce successes: 0.
- Every request has exactly three live-chain reads.
- The three locality generators are distinct and validated.
- `cache_hit` is measured per request; warmup state does not contaminate formal runs.
- Batch throughput uses a valid batch boundary.
- Inference uses paired run-level observations and 10,000 bootstrap resamples.
- The formal chain remained healthy after collection.
- The regression suite contains 97 passing tests.
- Repository secret scan: `TRUE_SECRET=0`, `UNCLASSIFIED=0`.

The preregistration JSON file contains a valid JSON object followed by a plain
text archival note. Its frozen bytes and index are intact, but the whole file is
not strict JSON. This is a non-material archival-format limitation and must not
be repaired by altering the frozen preregistration.

## Chain and deployment cross-check

The five formal Besu services were read-only checked as active. All report Besu
26.5.0 and Java 21. The chain ID is `2026072901`, peer count is four, the
validator set contains exactly four validators, and block height increased
during the audit. All five Genesis files match
`7d431f01aab7d0c55c58c09346ee1f9a43475322a4aca304cfbb172b9b32add4`.
The bytecode at `0x9ef44cf538d0df457ba77c556d8785e48bfc436d`
exactly matches the frozen deployed bytecode.

## Decision

No hard-stop condition was triggered. V13 is the sole valid formal performance
evidence for Research Content 2.
