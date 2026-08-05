# Attempt ID Root Cause

The failed value was `I9_P9_A_20260801T073550Z_793adab`.

The P9-A orchestration convention existed in `tests/r3/i9/test_p9a_contracts.py` as `I9_P9A_<UTC>_<git-short-sha>`, but the previous operational invocation manually constructed `I9_P9_A_<UTC>_<git-short-sha>`. Bootstrap accepted any non-empty argparse string and created directories before any shared identity validation.

Two independent validators then accepted only `I9_REVISION_`:

1. `src/epoch_auth_r3/pilot/config.py::attempt_scoped_run_id` used `startswith("I9_REVISION_")`.
2. `src/epoch_auth_r3/pilot/attempt.py::R3PilotAttemptIdentityV1.__post_init__` used the same independent prefix test.

Thus generation and validation were not one protocol. Revision 8 Canary passed because `I9_REVISION_8_20260730T155554Z_c1d9bbf` satisfied both legacy prefix checks. P9-A failed before runId generation because its family was not `REVISION` and the manually inserted extra underscore also differed from the P9-A test convention.

Legacy generation constraints were not formally centralized: bootstrap allowed arbitrary path text; the P9-A test convention used uppercase ASCII, underscores, UTC timestamp and seven lowercase hexadecimal Git characters; the runtime validator required only the fixed `I9_REVISION_` prefix. Minimum/maximum length, timestamp validity, path safety and exact suffix syntax were absent.

