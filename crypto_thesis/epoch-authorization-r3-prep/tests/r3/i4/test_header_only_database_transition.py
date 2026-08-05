from artifact_helpers import make_artifact


def test_header_only_keeps_body_and_key_versions(db):
    _,_,_,_,digest,_ = make_artifact(db, 1)
    make_artifact(db, 2, header_version=2, previous=digest)
    rows = db.execute(
        """SELECT header_version,body_version,key_version,update_kind::text,
                  encode(body_object_digest,'hex')
             FROM r3_control.header_version ORDER BY header_version"""
    ).fetchall()
    assert rows[0][1:4] == (1, 1, "INITIAL")
    assert rows[1][1:4] == (1, 1, "HEADER_ONLY")
    assert rows[0][4] == rows[1][4]
