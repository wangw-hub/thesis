import pytest
from epoch_auth_r3.database.job_repository import JobRepository
from conftest import event


@pytest.mark.parametrize("point",range(1,13),ids=lambda x:f"D{x}")
def test_d1_d12_transactions_never_partially_commit(db, point):
    before=db.execute("SELECT count(*) FROM r3_control.header_update_job").fetchone()[0]
    try:
        with db.transaction():
            if point >= 2:
                JobRepository(db).insert_event(event(point))
            if point >= 6:
                db.execute("""INSERT INTO r3_control.storage_object
                  (object_digest,backend,namespace,object_kind,size_bytes,reference_schema_version,verified)
                  VALUES (%s,'local','header','HEADER',1,1,true)""",(point.to_bytes(32,"big"),))
            raise RuntimeError(f"D{point}")
    except RuntimeError:
        pass
    assert db.execute("SELECT count(*) FROM r3_control.header_update_job").fetchone()[0]==before
    assert db.execute("SELECT count(*) FROM r3_control.storage_object").fetchone()[0]==0
