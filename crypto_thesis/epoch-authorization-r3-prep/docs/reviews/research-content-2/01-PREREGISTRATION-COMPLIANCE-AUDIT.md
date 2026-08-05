# R2-1 Preregistration Compliance Audit

## Decision

**MATERIAL_PROTOCOL_DEVIATION. Formal conclusions are stopped pending a complete rerun.**

## Findings

1. The collector performs one `eth_getBlock` at process startup and reuses that
   `chain_read_ns`, block number, block hash, and base fee for all 103,680 rows.
   Per-request live chain-state reading was not measured.
2. Issuer and verifier use an in-process `FrozenStore`, not `BesuStateGateway`.
   The data therefore do not measure the advertised complete live-chain state path.
3. The request generator does not branch on `locality`; rows labelled uniform,
   interval hotspot, and node hotspot use the same deterministic slot formula.
4. `throughput_rps` is calculated as the inverse of each request latency, rather
   than completed requests divided by measured batch duration.
5. `cache_hit` is derived from whether cumulative cache hits are greater than zero,
   not whether the current request hit the cache.
6. A separate pre-issue matcher invocation changes cache state before the timed
   issuance path, so cached and uncached paths do not represent the preregistered
   request lifecycle fairly.
7. Existing bootstrap intervals and effect sizes treat request rows as independent,
   despite the nested config/seed/repetition/request design.

Items 1-6 require a complete formal rerun. Item 7 can be corrected by run-level
paired analysis after valid data exist.

No raw rows may be deleted or rewritten. The current run is retained as
`INVALIDATED_MATERIAL_PROTOCOL_DEVIATION`.
