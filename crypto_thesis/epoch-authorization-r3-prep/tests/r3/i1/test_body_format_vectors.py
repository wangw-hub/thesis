from epoch_auth_r3.body.chunk_crypto import NonceUseRegistry
from epoch_auth_r3.body.format_v1 import decrypt_body, encrypt_body

CK = bytes(range(32))
RID = "ab" * 32


def enc(data, size=8):
    return encrypt_body(plaintext=data, ck=CK, nonce_base=b"12345678", chain_id=1337,
                        resource_id=RID, body_version=1, chunk_size=size,
                        nonce_registry=NonceUseRegistry())


def test_single_multi_empty_nonintegral_roundtrip():
    for data, size in [(b"x", 8), (b"0123456789abcdef", 4), (b"", 8), (b"12345", 4)]:
        assert decrypt_body(enc(data, size), CK) == data


def test_project_format_vector_is_deterministic():
    assert enc(b"project-format-vector", 5) == enc(b"project-format-vector", 5)
