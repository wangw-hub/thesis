# P9-A Gate Reconciliation

The failed attempt's local derived state is `P9_A_FAILED_STOPPED`; its immutable remote state file is `P9_A_RUNNING` because the old runner wrote RUNNING before runId generation and had no stage-level exception terminalizer. The exception bypassed all per-run terminalization and the final gate write.

The historical state file is not modified. Its SHA-256 is `0c45f13381686ed5c32867604edba3ba8343b0f30b4d19000e26e15b98435ee1`. The reconciliation derives `REMOTE_GATE_DERIVED_FINAL_STATE=P9_A_FAILED` from the preserved exception and zero-side-effect audit.

New attempts use `P9AStageTerminalizerV1`; a simulated top-level exception must end in `P9_A_FAILED`, and a completed process may not retain READY or RUNNING.

