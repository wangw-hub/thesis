# PilotEvidenceClassificationV1

The shared immutable model contains `pilotOnly`, `pilotPhase`, `scenarioClass`, `formalResultEligible`, and `performanceClaimEligible`. For P9-A it serializes exactly `PILOT_ONLY`, `P9_A_SMOKE_ONLY`, `NOT_FOR_FORMAL_THESIS_RESULTS`, and `NOT_FOR_PERFORMANCE_CLAIMS`.

The single producer is `PilotEvidenceClassificationV1.for_stage()`. It feeds config, common runtime context, final evidence, and strict validation. P9-B receives `P9_B`; development receives `DEVELOPMENT_ONLY/NOT_PILOT_EVIDENCE` and cannot inherit the smoke label.
