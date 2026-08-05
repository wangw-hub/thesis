import pytest
from epoch_auth_r3.database.exceptions import StaleWriteRejected
from epoch_auth_r3.database.job_repository import JobRepository
from epoch_auth_r3.database.models import JobStatus
from conftest import event


def test_stale_worker_cannot_submit(db):
    repo=JobRepository(db); repo.insert_event(event())
    job,_,version,_=repo.claim_jobs("w",1,60)[0]
    repo.cas(job,JobStatus.CLAIMED,version,JobStatus.RETRY_WAIT)
    with pytest.raises(StaleWriteRejected):
        repo.cas(job,JobStatus.CLAIMED,version,JobStatus.CANDIDATE_STORED,
                 candidate_header_digest=b"h"*32,candidate_header_object_digest=b"o"*32)
