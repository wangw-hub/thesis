from epoch_auth_r3.database.connection import DatabaseConfig


def test_i4_entry_is_loopback_postgresql(db):
    cfg = DatabaseConfig.from_environment()
    assert cfg.host in {"127.0.0.1", "localhost"}
    version = db.execute("SHOW server_version").fetchone()[0]
    assert version.startswith("16.")
    assert db.execute("SELECT current_schema").fetchone() is not None
