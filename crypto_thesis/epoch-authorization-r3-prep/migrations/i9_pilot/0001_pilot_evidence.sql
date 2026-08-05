CREATE SCHEMA IF NOT EXISTS r3_pilot AUTHORIZATION epoch_auth_r3_i9_pilot;

CREATE TABLE r3_pilot.pilot_run (
 run_id text PRIMARY KEY CHECK (run_id ~ '^[0-9a-f]{64}$'),
 run_group text NOT NULL,
 scenario_class text NOT NULL,
 seed bigint NOT NULL,
 config_digest text NOT NULL CHECK (config_digest ~ '^[0-9a-f]{64}$'),
 status text NOT NULL,
 valid boolean NOT NULL,
 start_block bigint,
 end_block bigint,
 raw_manifest_digest text NOT NULL CHECK (raw_manifest_digest ~ '^[0-9a-f]{64}$'),
 classification text NOT NULL DEFAULT 'PILOT_ONLY' CHECK (classification='PILOT_ONLY'),
 created_at timestamptz NOT NULL DEFAULT clock_timestamp()
);

CREATE TABLE r3_pilot.pilot_phase_event (
 run_id text NOT NULL REFERENCES r3_pilot.pilot_run(run_id),
 phase_sequence integer NOT NULL CHECK (phase_sequence >= 0),
 phase_name text NOT NULL,
 event_payload jsonb NOT NULL,
 PRIMARY KEY(run_id, phase_sequence)
);

REVOKE ALL ON SCHEMA r3_pilot FROM PUBLIC;
