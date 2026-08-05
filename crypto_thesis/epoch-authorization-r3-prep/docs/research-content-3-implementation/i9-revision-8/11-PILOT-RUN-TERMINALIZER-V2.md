# PilotRunTerminalizerV2

V2 consumes the append-only accumulator, identifies the deepest completed phase, and seals failure context, transaction evidence, object evidence, database evidence, phase analysis, payload hashes, envelope hash, and final artifact hashes. It emits `EVIDENCE_SEAL_COMPLETED` and `RUN_FINISHED` for failed as well as successful runs.
