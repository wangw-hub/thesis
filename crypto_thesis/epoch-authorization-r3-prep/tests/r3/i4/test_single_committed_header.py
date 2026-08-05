import pytest
from psycopg.errors import UniqueViolation
from artifact_helpers import make_artifact


def test_only_one_committed_header_per_resource(db):
    ev,_,_,_,d1,h1=make_artifact(db,1)
    _,_,_,_,_,h2=make_artifact(db,2,header_version=2,previous=d1)
    with db.transaction():
        db.execute("""UPDATE r3_control.header_version SET status='COMMITTED',
          committed_at=clock_timestamp() WHERE header_version_id=%s""",(h1,))
    with pytest.raises(UniqueViolation):
        with db.transaction():
            db.execute("""UPDATE r3_control.header_version SET status='COMMITTED',
              committed_at=clock_timestamp() WHERE header_version_id=%s""",(h2,))
