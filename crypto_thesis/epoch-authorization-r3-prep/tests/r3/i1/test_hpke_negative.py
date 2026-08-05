import pytest
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
from epoch_auth_r3.crypto.exceptions import IntegrityError
from epoch_auth_r3.crypto.hpke_provider import PyHPKEProvider

SKR = bytes.fromhex("4612c550263fc8ad58375df3f557aac531d26850903e55a9f23f21d8534e8ac8")
PKR = bytes.fromhex("3948cfe0ad1ddb695d780e59077195da6c56506b027329794ab02bca80815c4d")


@pytest.mark.parametrize("mutation", ["key", "enc", "ct", "aad", "info", "truncate", "extend"])
def test_negative_inputs_fail_closed(mutation):
    p = PyHPKEProvider()
    result = p.seal_base(PKR, b"test-only-ck" * 2, b"info", b"aad")
    key, enc, ct, info, aad = SKR, result.enc, result.ciphertext, b"info", b"aad"
    if mutation == "key": key = b"\x01" * 32
    elif mutation == "enc": enc = bytes([enc[0] ^ 1]) + enc[1:]
    elif mutation == "ct": ct = bytes([ct[0] ^ 1]) + ct[1:]
    elif mutation == "aad": aad = b"bad"
    elif mutation == "info": info = b"bad"
    elif mutation == "truncate": ct = ct[:-1]
    else: ct += b"\x00"
    with pytest.raises(IntegrityError):
        p.open_base(key, enc, ct, info, aad)


def test_empty_plaintext_and_distinct_recipients():
    p = PyHPKEProvider()
    empty = p.seal_base(PKR, b"", b"i", b"a")
    assert p.open_base(SKR, empty.enc, empty.ciphertext, b"i", b"a") == b""
    second_key = bytes.fromhex("5612c550263fc8ad58375df3f557aac531d26850903e55a9f23f21d8534e8ac8")
    second_pub = X25519PrivateKey.from_private_bytes(second_key).public_key().public_bytes_raw()
    a = p.seal_base(PKR, b"x" * 32, b"i", b"a")
    b = p.seal_base(second_pub, b"x" * 32, b"i", b"a")
    assert a.enc != b.enc
