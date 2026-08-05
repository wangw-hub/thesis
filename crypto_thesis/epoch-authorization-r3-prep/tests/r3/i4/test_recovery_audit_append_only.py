import pytest
from psycopg.errors import ObjectNotInPrerequisiteState
from epoch_auth_r3.database.repositories import ArtifactRepository
from artifact_helpers import make_artifact


def test_recovery_audit_cannot_update_or_delete(db):
    _,job,_,_,_,_=make_artifact(db,1)
    aid=ArtifactRepository(db).audit(job,"RECOVER","CLAIMED","PENDING","LEASE_EXPIRED")
    with pytest.raises(ObjectNotInPrerequisiteState):
        with db.transaction(): db.execute("DELETE FROM r3_control.recovery_audit WHERE audit_id=%s",(aid,))
