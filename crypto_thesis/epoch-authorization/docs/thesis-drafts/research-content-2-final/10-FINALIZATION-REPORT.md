# Chapter Five Finalization Report

## Decision

`CHAPTER_FINALIZED_FROM_VALID_V13_EVIDENCE`

The final chapter uses only the valid V13 rerun and run-level paired inference.
It contains eight reproducible data figures, two mechanism diagrams, six data
tables, three formula groups and three algorithms.

The chapter freezes the following interpretation:

- live chain reads dominate end-to-end latency (98.66%-98.80%);
- concurrency is the main observed latency factor;
- fragmentation increases local matching cost but not stable end-to-end cost;
- hotspots increase hit rate without stable engineering benefit;
- C(P) is a derived IR and ablation/falsification object;
- RC2's core contribution is the auditable state-binding and multi-instance
  authorization control loop.

No raw data, experiment protocol, formal-chain asset, code, contract or RC3
worktree is changed. FATAL=0, MAJOR=0, MINOR=2 (closed).
