import pytest
from epoch_auth_r3.body.chunk_crypto import NonceUseRegistry, chunk_nonce
from epoch_auth_r3.crypto.exceptions import CryptoValidationError, NonceReuseError


def test_nonce_encoding_and_uint32_boundary():
    assert chunk_nonce(b"12345678", 1) == b"12345678\x00\x00\x00\x01"
    assert chunk_nonce(b"12345678", 2**32-1)[-4:] == b"\xff"*4
    for value in (-1, 2**32):
        with pytest.raises(CryptoValidationError): chunk_nonce(b"12345678", value)
    with pytest.raises(CryptoValidationError): chunk_nonce(b"short", 0)


def test_same_ck_nonce_space_cannot_be_reused():
    registry = NonceUseRegistry()
    registry.reserve(b"K"*32, b"12345678")
    with pytest.raises(NonceReuseError): registry.reserve(b"K"*32, b"12345678")
