from concurrent.futures import ThreadPoolExecutor
import pytest
from epoch_auth_r3.database.connection import connect
from epoch_auth_r3.database.job_repository import JobRepository
from conftest import event


@pytest.mark.parametrize("workers",[2,4,16])
def test_concurrent_workers_have_no_duplicate_or_missing_claims(db, workers):
    repo=JobRepository(db)
    expected={repo.insert_event(event(i))[1] for i in range(1,33)}
    def claim(n):
        c=connect()
        try: return [x[0] for x in JobRepository(c).claim_jobs(f"w{n}",32,60)]
        finally: c.close()
    with ThreadPoolExecutor(max_workers=workers) as pool:
        claimed=[x for part in pool.map(claim,range(workers)) for x in part]
    assert len(claimed)==len(set(claimed))==32
    assert set(claimed)==expected
