from epoch_auth_r3.database.job_repository import JobRepository
from epoch_auth_r3.database.models import InsertResult
from conftest import event


def test_duplicate_event_returns_same_job_without_attempt_increment(db):
    repo=JobRepository(db)
    a=repo.insert_event(event()); b=repo.insert_event(event())
    assert a[0] == InsertResult.CREATED and b[0] == InsertResult.EXISTING_IDENTICAL
    assert a[1] == b[1]
    assert db.execute("SELECT attempt_count FROM r3_control.header_update_job").fetchone()[0] == 0
