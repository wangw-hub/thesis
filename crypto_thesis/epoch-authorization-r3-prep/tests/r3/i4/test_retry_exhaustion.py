from epoch_auth_r3.database.job_repository import JobRepository
from epoch_auth_r3.database.models import JobStatus
from conftest import event


def test_retry_budget_can_enter_terminal_state(db):
    repo=JobRepository(db); repo.insert_event(event(),max_attempts=1)
    job,_,version,_=repo.claim_jobs("w",1,60)[0]
    assert repo.cas(job,JobStatus.CLAIMED,version,JobStatus.FAILED_TERMINAL,
                    last_error_code="INVALID_EVENT") == version+1
