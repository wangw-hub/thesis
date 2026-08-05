from epoch_auth_r3.header.digest import header_digest


def test_semantic_order_same_digest_and_field_change_changes_digest():
    a, b = {"schemaVersion": 1, "x": "é", "n": 2}, {"n": 2, "x": "é", "schemaVersion": 1}
    assert header_digest(a) == header_digest(b)
    assert header_digest(a) != header_digest({**a, "n": 3})
