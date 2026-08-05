from epoch_auth_r3.database.schema import apply_migrations


def test_migrations_are_idempotently_detected(db):
    assert apply_migrations(db) == []
    # I6-I8 add append-only migrations; all nine I4 migrations remain immutable.
    assert db.execute("SELECT count(*) FROM r3_control.schema_metadata").fetchone()[0] == 12
