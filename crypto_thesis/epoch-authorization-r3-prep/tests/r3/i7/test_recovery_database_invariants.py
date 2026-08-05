import uuid

import pytest
from psycopg.errors import CheckViolation, UniqueViolation


def test_recovery_run_completion_requires_timestamp(recovery_run):
    conn, run_id = recovery_run
    with pytest.raises(CheckViolation):
        with conn.transaction():
            conn.execute(
                "UPDATE r3_control.recovery_run SET status='COMPLETED' "
                "WHERE recovery_run_id=%s", (run_id,)
            )


def test_recovery_run_can_complete_and_release(recovery_run):
    conn, run_id = recovery_run
    with conn.transaction():
        conn.execute(
            "UPDATE r3_control.recovery_run SET status='COMPLETED',"
            "completed_at=clock_timestamp(),material_release_enabled=true "
            "WHERE recovery_run_id=%s", (run_id,)
        )
    row = conn.execute(
        "SELECT status,material_release_enabled FROM r3_control.recovery_run "
        "WHERE recovery_run_id=%s", (run_id,)
    ).fetchone()
    assert row == ("COMPLETED", True)


def test_snapshot_unique_per_run_and_resource(recovery_run):
    conn, run_id = recovery_run
    values = (
        uuid.uuid4(), run_id, bytes(32), 2026073005, 1, bytes([1])*32,
        "db-snapshot", bytes([2])*32, "CONSISTENT",
    )
    sql = (
        "INSERT INTO r3_control.recovery_snapshot"
        "(recovery_snapshot_id,recovery_run_id,resource_id,chain_id,block_number,"
        "block_hash,database_snapshot_id,snapshot_digest,disposition)"
        " VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    )
    with conn.transaction():
        conn.execute(sql, values)
    duplicate = (uuid.uuid4(),) + values[1:]
    with pytest.raises(UniqueViolation):
        with conn.transaction():
            conn.execute(sql, duplicate)


def test_issue_resolution_timestamp_consistent(recovery_run):
    conn, run_id = recovery_run
    issue_id = uuid.uuid4()
    with pytest.raises(CheckViolation):
        with conn.transaction():
            conn.execute(
                "INSERT INTO r3_control.reconciliation_issue"
                "(reconciliation_issue_id,recovery_run_id,issue_code,disposition,"
                "requires_manual_action,resolved,resolved_at)"
                " VALUES (%s,%s,'X','CONFLICT',true,false,clock_timestamp())",
                (issue_id, run_id),
            )


def test_backup_manifest_requires_nonnegative_size(recovery_db):
    with pytest.raises(CheckViolation):
        with recovery_db.transaction():
            recovery_db.execute(
                "INSERT INTO r3_control.object_backup_manifest"
                "(object_digest,object_kind,backup_id,size_bytes,verified,immutable_snapshot)"
                " VALUES (%s,'HEADER','b',-1,true,true)", (bytes([3])*32,)
            )


def test_backup_manifest_digest_unique(recovery_db):
    digest = bytes([4])*32
    with recovery_db.transaction():
        recovery_db.execute(
            "INSERT INTO r3_control.object_backup_manifest"
            "(object_digest,object_kind,backup_id,size_bytes,verified,immutable_snapshot)"
            " VALUES (%s,'BODY','b1',1,true,true)", (digest,)
        )
    with pytest.raises(UniqueViolation):
        with recovery_db.transaction():
            recovery_db.execute(
                "INSERT INTO r3_control.object_backup_manifest"
                "(object_digest,object_kind,backup_id,size_bytes,verified,immutable_snapshot)"
                " VALUES (%s,'BODY','b2',1,true,true)", (digest,)
            )
