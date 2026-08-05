from epoch_auth_r3.database.job_repository import JobRepository
from epoch_auth_r3.database.repositories import ArtifactRepository
from epoch_auth_r3.storage import LocalObjectStore, ObjectKind
from conftest import event


def test_local_header_object_to_database_record_closure(db, tmp_path):
    data=b'{"synthetic":"signed-header-test-object"}'
    ref=LocalObjectStore(tmp_path).put(data,namespace="header",object_kind=ObjectKind.HEADER)
    ev=event(); _,job,op=JobRepository(db).insert_event(ev)
    repo=ArtifactRepository(db)
    assert repo.put_storage_object(bytes.fromhex(ref.digest_hex),ref.namespace,
                                   ref.object_kind.value,ref.size_bytes,True)
    assert db.execute("""SELECT verified FROM r3_control.storage_object
      WHERE object_digest=%s""",(bytes.fromhex(ref.digest_hex),)).fetchone()[0]
