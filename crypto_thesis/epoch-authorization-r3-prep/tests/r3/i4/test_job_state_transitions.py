import pytest
from epoch_auth_r3.database.exceptions import InvalidTransition
from epoch_auth_r3.database.job_repository import JobRepository
from epoch_auth_r3.database.models import JobStatus
from conftest import event


def test_illegal_transition_rejected_before_sql(db):
    repo=JobRepository(db); _,job,_=repo.insert_event(event())
    with pytest.raises(InvalidTransition):
        repo.cas(job,JobStatus.PENDING,0,JobStatus.COMMITTED)
