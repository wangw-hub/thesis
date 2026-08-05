def test_isolated_database_contains_no_rc2_business_tables(db):
    names={r[0] for r in db.execute("""SELECT table_name FROM information_schema.tables
      WHERE table_schema='public'""").fetchall()}
    assert not names
    assert db.execute("SELECT current_database()").fetchone()[0]=="epoch_auth_r3_i4_test"
