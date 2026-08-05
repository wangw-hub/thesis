import os
import uuid

import pytest

from epoch_auth_r3.database.connection import connect
from epoch_auth_r3.database.schema import apply_migrations


@pytest.fixture
def recovery_db():
    if not os.environ.get("R3_I4_PGPASSFILE"):
        pytest.skip("isolated PostgreSQL credential not supplied")
    apply_migrations()
    conn = connect()
    with conn.transaction():
        conn.execute(
            "TRUNCATE r3_control.object_backup_manifest,"
            "r3_control.reconciliation_issue,r3_control.recovery_snapshot,"
            "r3_control.recovery_run CASCADE"
        )
    yield conn
    conn.close()


@pytest.fixture
def recovery_run(recovery_db):
    run_id = uuid.uuid4()
    recovery_db.execute(
        "INSERT INTO r3_control.recovery_run"
        "(recovery_run_id,mode,status) VALUES (%s,'RECONCILE_RESOURCE','STARTED')",
        (run_id,),
    )
    recovery_db.commit()
    return recovery_db, run_id
