import pytest

from epoch_auth_r3.blockchain.composite_decoder import CompositeDecodeError, CompositeStateDecoderV1


ADDRESS = "0x" + "12" * 20


def _anchor():
    return (b"o" * 32, b"r" * 32, b"p" * 32, 1, 1, 1, 1, 1, 0,
            b"0" * 32, b"h" * 32, b"a" * 32, b"b" * 32, ADDRESS, 3, True)


def test_composite_state_decoder_exact_shape():
    decoded = CompositeStateDecoderV1.decode_anchor(_anchor())
    assert decoded.header_version == decoded.body_version == decoded.key_version == 1


def test_composite_state_decoder_missing_field():
    with pytest.raises(CompositeDecodeError, match="HEADER_ANCHOR_SHAPE"):
        CompositeStateDecoderV1.decode_anchor(_anchor()[:-1])


def test_composite_state_decoder_extra_field():
    with pytest.raises(CompositeDecodeError, match="HEADER_ANCHOR_SHAPE"):
        CompositeStateDecoderV1.decode_anchor(_anchor() + (None,))


def test_composite_state_decoder_wrong_type():
    value = list(_anchor()); value[5] = "1"
    with pytest.raises(CompositeDecodeError, match="HEADER_ANCHOR_HEADER_VERSION_UINT"):
        CompositeStateDecoderV1.decode_anchor(tuple(value))
