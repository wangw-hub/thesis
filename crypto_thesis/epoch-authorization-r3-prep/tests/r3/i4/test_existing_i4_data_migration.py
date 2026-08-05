def test_existing_i4_rows_receive_body_version_and_update_kind(db):
    columns = {row[0] for row in db.execute(
        """SELECT column_name FROM information_schema.columns
           WHERE table_schema='r3_control' AND table_name='header_version'"""
    ).fetchall()}
    assert {"body_version", "update_kind", "body_object_digest"} <= columns
    assert db.execute(
        "SELECT count(*) FROM r3_control.schema_metadata WHERE version=8"
    ).fetchone()[0] == 1
