from epoch_auth_r3.database.job_repository import JobRepository
from conftest import event


def test_expired_lease_is_recovered_and_audited(db):
    repo=JobRepository(db); _,job,_=repo.insert_event(event())
    repo.claim_jobs("old",1,60)
    with db.transaction():
        db.execute("""UPDATE r3_control.header_update_job
          SET lease_expires_at=clock_timestamp()-interval '1 second',
              row_version=row_version+1 WHERE job_id=%s""",(job,))
    assert repo.recover_expired()==[job]
    assert db.execute("SELECT count(*) FROM r3_control.recovery_audit").fetchone()[0]==1
