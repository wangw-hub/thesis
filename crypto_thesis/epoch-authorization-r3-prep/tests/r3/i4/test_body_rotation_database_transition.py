from artifact_helpers import make_artifact


def test_body_rotation_changes_body_and_key_together(db):
    _,_,_,_,digest,_ = make_artifact(db, 1)
    make_artifact(
        db, 2, header_version=2, previous=digest, body_version=2,
        key_version=2, update_kind="BODY_ROTATION", body_object=b"z" * 32,
    )
    row = db.execute(
        """SELECT body_version,key_version,update_kind::text
             FROM r3_control.header_version WHERE header_version=2"""
    ).fetchone()
    assert row == (2, 2, "BODY_ROTATION")
