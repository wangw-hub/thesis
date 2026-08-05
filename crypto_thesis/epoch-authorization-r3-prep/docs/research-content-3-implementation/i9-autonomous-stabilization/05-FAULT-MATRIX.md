# F1-F8 Fault Matrix

Authoritative pre-freeze run: `DEV_FAULT_20260801T141800Z_26cc5e9`.

F1 uncommitted JOB_CREATE: chain writes 0 PASS. F2 authorization ahead: HEADER_UPDATE_PENDING PASS. F3 incomplete recipient index: FAIL_CLOSED PASS. F4 Kubo unavailable: no restore/release PASS. F5 missing local plus valid replica: restore PASS. F6 stale intent: FAIL_CLOSED PASS. F7 broadcast/receipt unavailable: COMMIT_UNKNOWN evidence complete PASS. F8 A7 chain-stage failure: early 1/1/1/1 counts preserved PASS.
