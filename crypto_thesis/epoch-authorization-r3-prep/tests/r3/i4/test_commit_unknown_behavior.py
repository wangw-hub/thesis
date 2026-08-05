from epoch_auth_r3.database.repositories import ArtifactRepository
from artifact_helpers import make_artifact


def test_unknown_is_persisted_and_not_rebroadcast(db):
    _,job,op,_,_,_=make_artifact(db,1)
    repo=ArtifactRepository(db); aid=repo.add_commit_attempt(job,op,1)
    repo.set_commit_attempt(aid,"PREPARED","BROADCAST_UNKNOWN")
    assert db.execute("SELECT status FROM r3_control.commit_attempt").fetchone()[0]=="BROADCAST_UNKNOWN"
    assert db.execute("SELECT count(*) FROM r3_control.commit_attempt").fetchone()[0]==1
