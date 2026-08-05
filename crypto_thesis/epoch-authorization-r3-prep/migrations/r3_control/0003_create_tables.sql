CREATE TABLE r3_control.revocation_event_cursor (
 source_id text PRIMARY KEY,
 chain_id bigint NOT NULL CHECK (chain_id >= 0),
 authorization_contract r3_control.bytes20 NOT NULL,
 next_block_number bigint NOT NULL CHECK (next_block_number >= 0),
 next_log_index integer NOT NULL CHECK (next_log_index >= 0),
 last_processed_block_number bigint,
 last_processed_block_hash r3_control.bytes32,
 version bigint NOT NULL DEFAULT 0 CHECK (version >= 0),
 created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
 updated_at timestamptz NOT NULL DEFAULT clock_timestamp(),
 CHECK ((last_processed_block_number IS NULL) = (last_processed_block_hash IS NULL))
);

CREATE TABLE r3_control.header_update_job (
 job_id uuid PRIMARY KEY,
 operation_id r3_control.bytes32 NOT NULL UNIQUE,
 chain_id bigint NOT NULL CHECK (chain_id >= 0),
 authorization_contract r3_control.bytes20 NOT NULL,
 header_registry r3_control.bytes20 NOT NULL,
 event_signature r3_control.bytes32 NOT NULL,
 event_tx_hash r3_control.bytes32 NOT NULL,
 event_log_index integer NOT NULL CHECK (event_log_index >= 0),
 event_block_number bigint NOT NULL CHECK (event_block_number >= 0),
 event_block_hash r3_control.bytes32 NOT NULL,
 resource_id r3_control.bytes32 NOT NULL,
 target_epoch bigint NOT NULL CHECK (target_epoch >= 0),
 target_state_version bigint NOT NULL CHECK (target_state_version >= 0),
 target_header_version bigint NOT NULL CHECK (target_header_version > 0),
 target_key_version bigint NOT NULL CHECK (target_key_version > 0),
 status r3_control.job_status NOT NULL DEFAULT 'PENDING',
 attempt_count integer NOT NULL DEFAULT 0 CHECK (attempt_count >= 0),
 max_attempts integer NOT NULL DEFAULT 3 CHECK (max_attempts BETWEEN 1 AND 100),
 available_at timestamptz NOT NULL DEFAULT clock_timestamp(),
 lease_owner text,
 lease_expires_at timestamptz,
 row_version bigint NOT NULL DEFAULT 0 CHECK (row_version >= 0),
 candidate_header_digest r3_control.bytes32,
 candidate_header_object_digest r3_control.bytes32,
 last_error_code text,
 last_error_summary text CHECK (length(last_error_summary) <= 512),
 created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
 updated_at timestamptz NOT NULL DEFAULT clock_timestamp(),
 completed_at timestamptz,
 CHECK ((lease_owner IS NULL) = (lease_expires_at IS NULL)),
 CHECK (status <> 'CLAIMED' OR lease_owner IS NOT NULL),
 CHECK (status NOT IN ('CANDIDATE_STORED','READY_FOR_CHAIN_COMMIT','COMMIT_UNKNOWN','COMMITTED')
        OR (candidate_header_digest IS NOT NULL AND candidate_header_object_digest IS NOT NULL)),
 CHECK (status <> 'COMMITTED' OR completed_at IS NOT NULL)
);

CREATE TABLE r3_control.storage_object (
 object_digest r3_control.bytes32 PRIMARY KEY,
 backend text NOT NULL CHECK (backend = 'local'),
 namespace text NOT NULL CHECK (namespace ~ '^[a-z0-9_-]{1,64}$'),
 object_kind text NOT NULL CHECK (object_kind IN ('BODY','HEADER','GENERIC_TEST')),
 size_bytes bigint NOT NULL CHECK (size_bytes >= 0),
 reference_schema_version integer NOT NULL CHECK (reference_schema_version = 1),
 verified boolean NOT NULL,
 row_version bigint NOT NULL DEFAULT 0,
 created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
 updated_at timestamptz NOT NULL DEFAULT clock_timestamp(),
 UNIQUE (backend, namespace, object_kind, object_digest)
);

CREATE TABLE r3_control.header_version (
 header_version_id uuid PRIMARY KEY,
 job_id uuid NOT NULL UNIQUE REFERENCES r3_control.header_update_job(job_id),
 operation_id r3_control.bytes32 NOT NULL UNIQUE,
 resource_id r3_control.bytes32 NOT NULL,
 header_version bigint NOT NULL CHECK (header_version > 0),
 key_version bigint NOT NULL CHECK (key_version > 0),
 epoch bigint NOT NULL CHECK (epoch >= 0),
 state_version bigint NOT NULL CHECK (state_version >= 0),
 header_digest r3_control.bytes32 NOT NULL UNIQUE,
 previous_header_digest r3_control.bytes32,
 header_object_digest r3_control.bytes32 NOT NULL REFERENCES r3_control.storage_object(object_digest),
 status r3_control.header_status NOT NULL DEFAULT 'CANDIDATE',
 row_version bigint NOT NULL DEFAULT 0,
 created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
 updated_at timestamptz NOT NULL DEFAULT clock_timestamp(),
 committed_at timestamptz,
 UNIQUE (resource_id, header_version),
 CHECK ((header_version = 1 AND previous_header_digest IS NULL) OR
        (header_version > 1 AND previous_header_digest IS NOT NULL)),
 CHECK (status <> 'COMMITTED' OR committed_at IS NOT NULL)
);

CREATE TABLE r3_control.commit_attempt (
 attempt_id uuid PRIMARY KEY,
 job_id uuid NOT NULL REFERENCES r3_control.header_update_job(job_id),
 operation_id r3_control.bytes32 NOT NULL,
 attempt_number integer NOT NULL CHECK (attempt_number > 0),
 status r3_control.commit_status NOT NULL,
 evidence_source text NOT NULL CHECK (evidence_source = 'TEST_DOUBLE_ONLY'),
 transaction_hash r3_control.bytes32,
 error_code text,
 row_version bigint NOT NULL DEFAULT 0,
 created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
 updated_at timestamptz NOT NULL DEFAULT clock_timestamp(),
 UNIQUE (operation_id, attempt_number),
 UNIQUE (transaction_hash)
);

CREATE TABLE r3_control.recovery_audit (
 audit_id uuid PRIMARY KEY,
 job_id uuid REFERENCES r3_control.header_update_job(job_id),
 action text NOT NULL,
 before_status r3_control.job_status,
 after_status r3_control.job_status,
 reason_code text NOT NULL,
 evidence_source text NOT NULL CHECK (evidence_source IN ('DATABASE','SYNTHETIC_TEST_FIXTURE','TEST_DOUBLE_ONLY')),
 actor text NOT NULL,
 created_at timestamptz NOT NULL DEFAULT clock_timestamp()
);

CREATE TABLE r3_control.dead_letter_job (
 dead_letter_id uuid PRIMARY KEY,
 job_id uuid NOT NULL UNIQUE REFERENCES r3_control.header_update_job(job_id),
 operation_id r3_control.bytes32 NOT NULL UNIQUE,
 terminal_error_code text NOT NULL,
 terminal_error_summary text CHECK (length(terminal_error_summary) <= 512),
 original_status r3_control.job_status NOT NULL,
 created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
 disposition text NOT NULL DEFAULT 'UNRESOLVED' CHECK (disposition IN ('UNRESOLVED','ACKNOWLEDGED'))
);
