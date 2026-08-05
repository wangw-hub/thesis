import pytest
from epoch_auth_r3.database.exceptions import StaleWriteRejected
from epoch_auth_r3.database.job_repository import JobRepository
from conftest import event


def test_lease_renewal_requires_owner_and_version(db):
    repo=JobRepository(db); repo.insert_event(event())
    job,_,version,_=repo.claim_jobs("owner",1,60)[0]
    assert repo.renew_lease(job,"owner",version,60)==version+1
    with pytest.raises(StaleWriteRejected): repo.renew_lease(job,"other",version+1,60)
