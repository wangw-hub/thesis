# EvidenceAccumulatorV1

Evidence is appended as fsynced JSON Lines throughout execution. Keys are immutable: a different value for an existing key is rejected. Transaction records are indexed and preserved before later stages can fail.

The accumulator contains no private keys, CK, passwords, or full DSNs.
