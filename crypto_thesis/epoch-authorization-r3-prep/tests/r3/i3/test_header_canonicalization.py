from epoch_auth_r3.header.models import SignedVersionedHeaderV1


def test_parse_serialize_is_unique(signed_header):
    data = signed_header.to_canonical_bytes()
    assert SignedVersionedHeaderV1.from_strict_json_bytes(data).to_canonical_bytes() == data
    assert b" " not in data and b"\n" not in data
