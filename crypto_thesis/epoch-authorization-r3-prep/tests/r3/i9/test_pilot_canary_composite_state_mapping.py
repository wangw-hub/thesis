from epoch_auth_r3.blockchain.composite_decoder import CompositeStateDecoderV1


def test_named_anchor_mapping_uses_frozen_field_order():
    value = (b"o" * 32, b"r" * 32, b"p" * 32, 1, 2, 3, 4, 4, 0,
             b"q" * 32, b"h" * 32, b"x" * 32, b"b" * 32,
             "0x" + "1" * 40, 5, True)
    anchor = CompositeStateDecoderV1.decode_anchor(value)
    assert anchor.header_version == 3
    assert anchor.body_version == anchor.key_version == 4
    assert anchor.header_digest == b"h" * 32
