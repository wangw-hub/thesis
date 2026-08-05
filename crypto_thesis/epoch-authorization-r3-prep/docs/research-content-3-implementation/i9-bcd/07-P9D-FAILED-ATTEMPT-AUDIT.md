# P9-D Attempt Audit — Frozen Invalid Attempt

The remote attempt `I9_P9D_20260801T162347Z_0d9a2e2` is immutable and excluded
from strict acceptance.  Its executor completed 24/24 runs, but the read-only
audit found a producer evidence defect in every `fault-evidence.json` record:
the required `FaultInjectionEvidenceV1` fields for independent injection and
observation were absent.  The two `KUBO_UNAVAILABLE` runs additionally used
`invalid-loopback-port` rather than a controlled isolated-service action.

This is classified as `EVIDENCE_DEFECT` / `AUTO_FIXABLE_DEFECT`, not a protocol
or scientific-design change.  No raw file in the failed attempt was modified.
The next attempt must use a new attempt ID, new run IDs, and a new executable
snapshot after producer repair.

Audit facts:

- raw fault files: 24
- unique run IDs: 24
- required-field-complete records: 0
- observation source `controlled-sentinel`: 22
- observation source `invalid-loopback-port`: 2
- historical raw mutation: 0

