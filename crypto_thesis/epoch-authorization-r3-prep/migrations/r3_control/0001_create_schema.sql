CREATE SCHEMA IF NOT EXISTS r3_control AUTHORIZATION epoch_auth_r3_i4_test;
CREATE TABLE IF NOT EXISTS r3_control.schema_metadata (
    version integer PRIMARY KEY CHECK (version > 0),
    migration_name text NOT NULL UNIQUE,
    migration_sha256 bytea NOT NULL CHECK (octet_length(migration_sha256) = 32),
    applied_at timestamptz NOT NULL DEFAULT clock_timestamp()
);
