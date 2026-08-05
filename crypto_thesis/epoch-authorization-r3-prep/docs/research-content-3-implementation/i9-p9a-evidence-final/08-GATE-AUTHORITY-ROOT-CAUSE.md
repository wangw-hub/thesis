# Gate authority root cause

The runner previously reduced business results to `StageQuality.passed()` and passed that boolean directly to `P9AStageTerminalizerV1.finish()` before strict evidence review. This allowed mechanical PASS with zero strictly valid runs.

The boolean entry was removed. The terminalizer now requires `P9AAcceptanceDecisionV1` and rejects decision/count mismatches.
