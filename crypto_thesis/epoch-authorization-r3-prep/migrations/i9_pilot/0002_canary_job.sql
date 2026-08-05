CREATE TABLE IF NOT EXISTS r3_pilot.pilot_canary_job (
 job_id text PRIMARY KEY CHECK (job_id ~ '^[0-9a-f]{64}$'),
 run_id text NOT NULL UNIQUE CHECK (run_id ~ '^[0-9a-f]{64}$'),
 status text NOT NULL CHECK (status IN ('CREATED', 'CHAIN_CONFIRMED', 'COMMITTED')),
 operation_id text NOT NULL UNIQUE CHECK (operation_id ~ '^[0-9a-f]{64}$'),
 header_digest text,
 body_digest text,
 created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
 committed_at timestamptz
);

GRANT SELECT, INSERT, UPDATE ON r3_pilot.pilot_canary_job TO epoch_auth_r3_i9_pilot;
