from epoch_auth_r3.header.schema_v1 import HPKE_SUITE


def test_envelope_has_no_private_key_or_plain_ck(signed_header):
    encoded = signed_header.to_canonical_bytes()
    assert len(signed_header.core.recipient_envelopes) == 2
    assert all(x.hpke_suite == HPKE_SUITE and len(x.enc) == 32 for x in signed_header.core.recipient_envelopes)
    assert b"C"*32 not in encoded and b"private" not in encoded.lower()
