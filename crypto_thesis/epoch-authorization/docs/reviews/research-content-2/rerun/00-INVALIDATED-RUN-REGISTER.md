# Invalidated Formal Run Register

Status: `INVALIDATED_IMMUTABLE`; the directory
`experiments/runs/formal_auth_multihost_20260729_34af4ff` remains read-only and
is excluded from every V2 inference.

| Issue | Severity | Affected evidence | Repair and closure gate |
|---|---|---|---|
| FATAL-1 | FATAL | chain read and end-to-end latency | Use `BesuStateGateway` for each request and require request-linked traces in unit tests and dry-run. |
| FATAL-2 | FATAL | locality and cache claims | Generate three deterministic but distributionally distinct slot sequences and validate hashes/hotspot rates. |
| MAJOR-1 | MAJOR | confidence intervals | Preserve workload pairing and use run-level paired bootstrap. |
| MAJOR-2 | MAJOR | throughput | Measure completed requests over actual batch start/end. |
| MAJOR-3 | MAJOR | cache hits | Record the explicit result of each cache lookup. |
| MAJOR-4 | MAJOR | cache latency | Remove untimed matcher calls and reset cache per measured repetition. |

No item is closed by this register alone. Closure requires automated tests and
V2 dry-run evidence.
