# Attempt ID Complete Audit

Production Python sources and I9 scripts were searched for `attemptId`, `attempt_id`, `INVALID_ATTEMPT_ID`, `ATTEMPT_ID`, regular expressions, `fullmatch`, `match`, validation and parsing symbols.

Before repair, runtime-reachable validators numbered two and both excluded P9-A. Bootstrap had no validator. P9-A matrix code generated a separate scenario-level digest without validating the attempt string.

After repair, all runtime-reachable validation routes call `PilotAttemptIdV1.validate`:

- `CANARY_SHARED_RUNTIME`: `R3PilotAttemptIdentityV1`, `attempt_scoped_run_id`;
- `P9_A_RUNTIME`: bootstrap, remote runner, P9-A scenario matrix and stage terminalizer;
- `P9_B_FUTURE`: inherits the remote runner validation but remains forbidden;
- `TEST_ONLY`: fixtures contain valid Revision or P9A examples;
- `DOCUMENTATION` and `HISTORICAL`: immutable evidence strings only.

Runtime validator implementations: 1. Conflicting runtime rules: 0. Unclassified hits: 0. Revision 8 remains parseable. The failed `I9_P9_A_...` value is permanently invalid and never reused.

