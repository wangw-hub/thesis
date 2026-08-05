from epoch_auth_r3.database.job_repository import JobRepository
from epoch_auth_r3.database.models import JobStatus
from conftest import event


def test_dead_letter_preserves_original_job(db):
    repo=JobRepository(db); repo.insert_event(event())
    job,_,v,_=repo.claim_jobs("w",1,60)[0]
    v=repo.cas(job,JobStatus.CLAIMED,v,JobStatus.FAILED_TERMINAL,last_error_code="INVALID_HEADER")
    repo.dead_letter(job,v,"INVALID_HEADER","synthetic")
    assert db.execute("SELECT count(*) FROM r3_control.header_update_job").fetchone()[0]==1
    assert db.execute("SELECT count(*) FROM r3_control.dead_letter_job").fetchone()[0]==1
