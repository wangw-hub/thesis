CREATE TYPE r3_control.recovery_disposition AS ENUM (
 'CONSISTENT','AUTO_RECOVERABLE','RETRYABLE_TRANSIENT',
 'MANUAL_RECONCILIATION_REQUIRED','FAIL_CLOSED_MISSING_OBJECT',
 'FAIL_CLOSED_CORRUPT_OBJECT','FAIL_CLOSED_KEY_UNAVAILABLE',
 'FAIL_CLOSED_CHAIN_UNAVAILABLE','FAIL_CLOSED_DATABASE_UNAVAILABLE',
 'IRRECOVERABLE_CONTENT_LOSS','IRRECOVERABLE_KEY_LOSS','SUPERSEDED',
 'ORPHANED_OBJECT','ORPHANED_DATABASE_RECORD','UNKNOWN_TRANSACTION',
 'CONFLICT','UNSUPPORTED'
);

CREATE TABLE r3_control.recovery_run (
 recovery_run_id uuid PRIMARY KEY,
 mode text NOT NULL CHECK (mode IN (
  'RECONCILE_RESOURCE','RECONCILE_OPERATION','RECONCILE_EVENT','RECONCILE_ALL_BOUNDED'
 )),
 status text NOT NULL CHECK (status IN ('STARTED','COMPLETED','FAILED','MANUAL_REQUIRED')),
 material_release_enabled boolean NOT NULL DEFAULT false,
 started_at timestamptz NOT NULL DEFAULT clock_timestamp(),
 completed_at timestamptz,
 CHECK (status='STARTED' OR completed_at IS NOT NULL),
 CHECK (status='STARTED' OR material_release_enabled=false OR status='COMPLETED')
);

CREATE TABLE r3_control.recovery_snapshot (
 recovery_snapshot_id uuid PRIMARY KEY,
 recovery_run_id uuid NOT NULL REFERENCES r3_control.recovery_run(recovery_run_id),
 resource_id r3_control.bytes32 NOT NULL,
 chain_id bigint NOT NULL,
 block_number bigint NOT NULL CHECK (block_number >= 0),
 block_hash r3_control.bytes32 NOT NULL,
 database_snapshot_id text NOT NULL,
 snapshot_digest r3_control.bytes32 NOT NULL,
 disposition r3_control.recovery_disposition NOT NULL,
 captured_at timestamptz NOT NULL DEFAULT clock_timestamp(),
 UNIQUE(recovery_run_id,resource_id)
);

CREATE TABLE r3_control.reconciliation_issue (
 reconciliation_issue_id uuid PRIMARY KEY,
 recovery_run_id uuid NOT NULL REFERENCES r3_control.recovery_run(recovery_run_id),
 resource_id r3_control.bytes32,
 operation_id r3_control.bytes32,
 issue_code text NOT NULL,
 disposition r3_control.recovery_disposition NOT NULL,
 requires_manual_action boolean NOT NULL,
 resolved boolean NOT NULL DEFAULT false,
 created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
 resolved_at timestamptz,
 CHECK ((resolved_at IS NOT NULL)=resolved)
);

CREATE TABLE r3_control.object_backup_manifest (
 object_digest r3_control.bytes32 PRIMARY KEY,
 object_kind text NOT NULL CHECK (object_kind IN ('HEADER','BODY')),
 backup_id text NOT NULL UNIQUE,
 size_bytes bigint NOT NULL CHECK(size_bytes >= 0),
 verified boolean NOT NULL,
 immutable_snapshot boolean NOT NULL,
 created_at timestamptz NOT NULL DEFAULT clock_timestamp()
);
