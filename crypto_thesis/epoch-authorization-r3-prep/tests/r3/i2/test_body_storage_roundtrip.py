from epoch_auth_r3.body.chunk_crypto import NonceUseRegistry
from epoch_auth_r3.body.format_v1 import decrypt_body, encrypt_body
from epoch_auth_r3.serialization.base64url import encode
from epoch_auth_r3.serialization.jcs_adapter import canonicalize
from epoch_auth_r3.storage import ObjectKind

CK = b"K" * 32


def body_bytes(envelope):
    return canonicalize({
        "bodyVersion": envelope.body_version, "chainId": envelope.chain_id,
        "chunkCount": envelope.chunk_count, "chunkSize": envelope.chunk_size,
        "chunks": [{"ciphertext": encode(c.ciphertext), "index": c.index, "plaintextLength": c.plaintext_length} for c in envelope.chunks],
        "formatVersion": envelope.format_version, "manifestDigest": encode(envelope.manifest_digest),
        "nonceBase": encode(envelope.nonce_base), "plaintextLength": envelope.plaintext_length,
        "resourceId": envelope.resource_id,
    })


def close(store, plaintext, chunk_size):
    env = encrypt_body(plaintext=plaintext, ck=CK, nonce_base=b"I2NONCE!", chain_id=1337,
                       resource_id="42"*32, body_version=1, chunk_size=chunk_size,
                       nonce_registry=NonceUseRegistry())
    data = body_bytes(env)
    ref = store.put(data, namespace="body", object_kind=ObjectKind.BODY)
    assert store.exists(ref) and store.verify(ref).verified and store.get(ref) == data
    assert decrypt_body(env, CK) == plaintext


def test_empty_single_multi_and_non_integral_body_closure(store):
    for plaintext, size in [(b"", 8), (b"x", 8), (b"0123456789abcdef", 4), (b"12345", 4)]:
        close(store, plaintext, size)
