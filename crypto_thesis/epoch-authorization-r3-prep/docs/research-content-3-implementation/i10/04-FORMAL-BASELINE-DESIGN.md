# Formal Baseline Design

Baseline-R is retained: identical workload and security semantics with `LOCAL_ONLY` object storage, compared only to matched `KUBO_REPLICA` blocks. Baseline-H (no versioned header/simple rebuild) is removed as unfair because it changes the state and security semantics. Baseline-U (alternative update strategy) is not frozen because no semantically equivalent independent implementation is available; it may not be invented after results are seen. HEADER_ONLY and BODY_ROTATION are semantic classes, never baselines for each other.
