# Smoke classification root cause

The attempt bootstrap manifest contained all four labels, but `run_revised_remote_pilot.py` created a separate three-string `LABELS` list. `R3PilotConfigV1` had no classification field, so the attempt classification could not propagate through config, runtime context, raw envelope, or strict validation. All eight runs used the same runner constant and therefore uniformly omitted `P9_A_SMOKE_ONLY`.

The validator requirement was retained; old raw was not patched.
