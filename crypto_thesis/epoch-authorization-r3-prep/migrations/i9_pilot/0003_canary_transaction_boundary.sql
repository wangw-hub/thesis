ALTER TABLE r3_pilot.pilot_canary_job
    DROP CONSTRAINT IF EXISTS pilot_canary_job_status_check;

ALTER TABLE r3_pilot.pilot_canary_job
    ADD COLUMN IF NOT EXISTS attempt_id text,
    ADD COLUMN IF NOT EXISTS resource_id text,
    ADD COLUMN IF NOT EXISTS update_kind text,
    ADD COLUMN IF NOT EXISTS header_object_digest text,
    ADD COLUMN IF NOT EXISTS body_object_digest text,
    ADD COLUMN IF NOT EXISTS chain_write_plan jsonb,
    ADD CONSTRAINT pilot_canary_job_status_check
        CHECK (status IN (
            'CREATED', 'READY_FOR_CHAIN_SUBMISSION',
            'CHAIN_CONFIRMED', 'COMMITTED'
        ));

CREATE UNIQUE INDEX IF NOT EXISTS pilot_canary_job_attempt_resource_uq
    ON r3_pilot.pilot_canary_job(attempt_id, resource_id);
