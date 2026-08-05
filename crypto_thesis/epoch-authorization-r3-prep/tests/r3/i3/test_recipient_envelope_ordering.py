from conftest import build_header, recipients


def test_builder_canonicalizes_recipient_order():
    header = build_header(recipient_list=list(reversed(recipients())))
    keys = [x.recipient_key_id for x in header.core.recipient_envelopes]
    assert keys == sorted(keys)
