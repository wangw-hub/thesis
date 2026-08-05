import pytest
from epoch_auth_r3.database.repositories import ArtifactRepository
from artifact_helpers import make_artifact


def test_commit_attempt_is_test_double_and_transitioned_cas_style(db):
    _,job,op,_,_,_=make_artifact(db,1)
    repo=ArtifactRepository(db)
    aid=repo.add_commit_attempt(job,op,1)
    assert repo.set_commit_attempt(aid,"PREPARED","CONFIRMED_TEST_DOUBLE")==1
    assert db.execute("SELECT evidence_source FROM r3_control.commit_attempt").fetchone()[0]=="TEST_DOUBLE_ONLY"
    with pytest.raises(ValueError): repo.set_commit_attempt(aid,"PREPARED","BROADCAST_UNKNOWN")
