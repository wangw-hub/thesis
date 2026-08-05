from epoch_auth_r3.database.job_repository import JobRepository
from conftest import event


def test_transaction_failure_leaves_no_partial_state(db):
    try:
        with db.transaction():
            JobRepository(db).insert_event(event())
            raise RuntimeError("synthetic crash")
    except RuntimeError:
        pass
    assert db.execute("SELECT count(*) FROM r3_control.header_update_job").fetchone()[0]==0
