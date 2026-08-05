from epoch_auth_r3.database.connection import connect
from epoch_auth_r3.database.job_repository import JobRepository
from conftest import event


def test_skip_locked_claims_another_job(db):
    repo=JobRepository(db)
    ids=[repo.insert_event(event(i))[1] for i in (1,2)]
    locker=connect()
    try:
        locker.execute("""SELECT job_id FROM r3_control.header_update_job
            WHERE job_id=%s FOR UPDATE""",(ids[0],))
        other=connect()
        try:
            claimed=JobRepository(other).claim_jobs("w",2,60)
            assert [x[0] for x in claimed] == [ids[1]]
        finally: other.close()
    finally:
        locker.rollback(); locker.close()
