-- Isolated Pilot database administrator only.
-- These are test-harness identities, never Pilot attempt identities.
DELETE FROM r3_pilot.pilot_canary_job
WHERE attempt_id IN (
    'REV8_PREFLIGHT_REV8-FBBEEB0',
    'REV8_PREFLIGHT_REV8-977590F',
    'REV8_PREFLIGHT_REV8-FINAL'
);
