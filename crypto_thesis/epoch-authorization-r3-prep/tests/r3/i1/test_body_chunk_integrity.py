from dataclasses import replace
import pytest
from epoch_auth_r3.body.chunk_crypto import NonceUseRegistry
from epoch_auth_r3.body.format_v1 import decrypt_body, encrypt_body
from epoch_auth_r3.crypto.exceptions import CryptoValidationError, IntegrityError

CK = b"K" * 32
ENV = encrypt_body(plaintext=b"abcdefghijklmnop", ck=CK, nonce_base=b"NONCE123",
                   chain_id=9, resource_id="12" * 32, body_version=4, chunk_size=4,
                   nonce_registry=NonceUseRegistry())


@pytest.mark.parametrize("variant", [
    replace(ENV, chunks=(replace(ENV.chunks[0], ciphertext=b"x"+ENV.chunks[0].ciphertext[1:]),)+ENV.chunks[1:]),
    replace(ENV, chunks=(ENV.chunks[1], ENV.chunks[0])+ENV.chunks[2:]),
    replace(ENV, chunks=ENV.chunks[:-1]),
    replace(ENV, chunks=(ENV.chunks[0], ENV.chunks[0])+ENV.chunks[2:]),
    replace(ENV, chunks=ENV.chunks[:-1]+(replace(ENV.chunks[-1], ciphertext=ENV.chunks[-1].ciphertext[:-1]),)),
    replace(ENV, plaintext_length=17),
    replace(ENV, resource_id="13"*32),
    replace(ENV, body_version=5),
    replace(ENV, nonce_base=b"NONCE124"),
])
def test_tamper_reorder_delete_duplicate_truncate_append_and_context_rejected(variant):
    with pytest.raises((IntegrityError, CryptoValidationError)):
        decrypt_body(variant, CK)


def test_wrong_ck_and_cross_resource_version_rejected():
    with pytest.raises(IntegrityError): decrypt_body(ENV, b"Q"*32)
