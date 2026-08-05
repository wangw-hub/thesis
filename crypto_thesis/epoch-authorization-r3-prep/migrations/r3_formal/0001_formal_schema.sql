-- Independent Formal database schema (R3 I11).  No Pilot/RC2 namespaces.
CREATE SCHEMA IF NOT EXISTS r3_formal AUTHORIZATION epoch_auth_r3_formal;

CREATE TABLE IF NOT EXISTS r3_formal.formal_run (
 run_id text PRIMARY KEY CHECK (run_id ~ '^[0-9a-f]{64}$'),
 attempt_id text NOT NULL CHECK (attempt_id ~ '^FORMAL_[0-9]{8}T[0-9]{6}Z_[0-9a-f]{7}$'),
 experiment_id text NOT NULL CHECK (experiment_id IN ('E1','E2','E3','E4','E5','WARMUP')),
 scenario_class text NOT NULL,
 semantic_class text NOT NULL,
 config_digest text NOT NULL CHECK (config_digest ~ '^[0-9a-f]{64}$'),
 repeat_index integer NOT NULL CHECK (repeat_index > 0),
 warmup boolean NOT NULL,
 status text NOT NULL,
 valid boolean NOT NULL,
 disposition text NOT NULL,
 start_block bigint,
 end_block bigint,
 raw_manifest_digest text NOT NULL CHECK (raw_manifest_digest ~ '^[0-9a-f]{64}$'),
 classification text NOT NULL DEFAULT 'FORMAL_EXPERIMENT'
   CHECK (classification = 'FORMAL_EXPERIMENT'),
 created_at timestamptz NOT NULL DEFAULT clock_timestamp()
);

CREATE TABLE IF NOT EXISTS r3_formal.formal_phase_event (
 run_id text NOT NULL REFERENCES r3_formal.formal_run(run_id),
 phase_sequence integer NOT NULL CHECK (phase_sequence >= 0),
 phase_name text NOT NULL,
 event_payload jsonb NOT NULL,
 PRIMARY KEY (run_id, phase_sequence)
);

CREATE TABLE IF NOT EXISTS r3_formal.formal_run_job (
 job_id text PRIMARY KEY CHECK (job_id ~ '^[0-9a-f]{64}$'),
 run_id text NOT NULL UNIQUE CHECK (run_id ~ '^[0-9a-f]{64}$'),
 attempt_id text NOT NULL,
 status text NOT NULL CHECK (status IN (
   'CREATED', 'READY_FOR_CHAIN_SUBMISSION', 'CHAIN_CONFIRMED', 'COMMITTED'
 )),
 operation_id text NOT NULL UNIQUE CHECK (operation_id ~ '^[0-9a-f]{64}$'),
 resource_id text NOT NULL,
 update_kind text NOT NULL,
 header_digest text,
 header_object_digest text,
 body_digest text,
 body_object_digest text,
 chain_write_plan jsonb,
 created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
 committed_at timestamptz
);

CREATE UNIQUE INDEX IF NOT EXISTS formal_run_job_attempt_resource_uq
    ON r3_formal.formal_run_job(attempt_id, resource_id);

GRANT SELECT, INSERT, UPDATE ON r3_formal.formal_run TO epoch_auth_r3_formal;
GRANT SELECT, INSERT, UPDATE ON r3_formal.formal_phase_event TO epoch_auth_r3_formal;
GRANT SELECT, INSERT, UPDATE ON r3_formal.formal_run_job TO epoch_auth_r3_formal;
REVOKE ALL ON SCHEMA r3_formal FROM PUBLIC;
