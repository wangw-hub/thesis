def test_header_replication_exact_readback(i8_fixture):
    record = i8_fixture["gateway"].replicate(i8_fixture["header_ref"])
    assert i8_fixture["gateway"].fetch_verified(i8_fixture["header_ref"], record) == i8_fixture["header_bytes"]


def test_body_replication_exact_readback(i8_fixture):
    record = i8_fixture["gateway"].replicate(i8_fixture["body_ref"])
    assert i8_fixture["gateway"].fetch_verified(i8_fixture["body_ref"], record) == i8_fixture["body_bytes"]


def test_same_bytes_same_profile_same_cid(i8_fixture):
    first = i8_fixture["gateway"].replicate(i8_fixture["body_ref"])
    second = i8_fixture["gateway"].replicate(i8_fixture["body_ref"])
    assert first.cid == second.cid


def test_header_pin_confirmed(i8_fixture):
    record = i8_fixture["gateway"].replicate(i8_fixture["header_ref"])
    assert record.pin_status and i8_fixture["client"].pin_ls(record.cid)


def test_body_pin_confirmed(i8_fixture):
    record = i8_fixture["gateway"].replicate(i8_fixture["body_ref"])
    assert record.pin_status and i8_fixture["client"].pin_ls(record.cid)
