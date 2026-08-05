from concurrent.futures import ThreadPoolExecutor
from epoch_auth_r3.database.connection import connect
from epoch_auth_r3.database.exceptions import StaleWriteRejected
from epoch_auth_r3.database.job_repository import JobRepository
from epoch_auth_r3.database.models import JobStatus
from conftest import event


def test_only_one_competing_cas_succeeds(db):
    repo=JobRepository(db); repo.insert_event(event())
    job,_,version,_=repo.claim_jobs("w",1,60)[0]
    def update(_):
        c=connect()
        try:
            JobRepository(c).cas(job,JobStatus.CLAIMED,version,JobStatus.RETRY_WAIT)
            return True
        except StaleWriteRejected: return False
        finally: c.close()
    with ThreadPoolExecutor(max_workers=2) as p:
        assert sum(p.map(update,range(2)))==1
