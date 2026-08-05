import pytest
from psycopg.errors import CheckViolation

from artifact_helpers import make_artifact


def test_header_only_cannot_change_body_digest(db):
    _,_,_,_,digest,_ = make_artifact(db, 1)
    with pytest.raises(CheckViolation):
        make_artifact(
            db, 2, header_version=2, previous=digest,
            update_kind="HEADER_ONLY", body_object=b"y" * 32,
        )


def test_body_rotation_must_change_body_digest(db):
    _,_,_,_,digest,_ = make_artifact(db, 1)
    prior = bytes(db.execute(
        "SELECT body_object_digest FROM r3_control.header_version WHERE header_version=1"
    ).fetchone()[0])
    with pytest.raises(CheckViolation):
        make_artifact(
            db, 2, header_version=2, previous=digest, body_version=2,
            key_version=2, update_kind="BODY_ROTATION", body_object=prior,
        )
