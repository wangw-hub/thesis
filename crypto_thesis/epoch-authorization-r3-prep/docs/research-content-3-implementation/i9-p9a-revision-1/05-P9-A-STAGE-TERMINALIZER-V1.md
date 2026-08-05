# P9AStageTerminalizerV1

`P9AStageTerminalizerV1` owns P9-A gate transitions:

`P9_A_READY -> P9_A_RUNNING -> P9_A_PASSED|P9_A_FAILED`.

It validates the attempt identity, validates the prior gate and attempt binding, performs revision-based compare-and-swap checking, writes through `AtomicJsonWriterV1`, fsyncs, reads back, verifies the final SHA, and emits `p9a-stage-gate-evidence.json`.

Top-level orchestration exceptions are terminalized even before a run exists. Such failures record `failureScope=ATTEMPT_ORCHESTRATION`, `failedScenario=A1`, `runCreated=false`, and `businessSideEffects=false`; they do not fabricate a failed business run. Scenario failure stops the serial loop and cannot leave `P9_A_RUNNING`.

