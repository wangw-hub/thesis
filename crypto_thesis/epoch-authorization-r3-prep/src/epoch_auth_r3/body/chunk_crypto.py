from __future__ import annotations

import hashlib

from epoch_auth_r3.crypto.aead import aes256_gcm_decrypt, aes256_gcm_encrypt
from epoch_auth_r3.crypto.exceptions import CryptoValidationError, NonceReuseError
from epoch_auth_r3.serialization.base64url import encode
from epoch_auth_r3.serialization.jcs_adapter import canonicalize


def chunk_nonce(nonce_base: bytes, chunk_index: int) -> bytes:
    if len(nonce_base) != 8:
        raise CryptoValidationError("nonceBase must be 8 bytes")
    if not 0 <= chunk_index < 2**32:
        raise CryptoValidationError("chunkIndex outside uint32 range")
    return nonce_base + chunk_index.to_bytes(4, "big")


def chunk_aad(
    *,
    chain_id: int,
    resource_id: str,
    body_version: int,
    manifest_digest: bytes,
    chunk_index: int,
    chunk_count: int,
    plaintext_length: int,
    chunk_plaintext_length: int,
) -> bytes:
    return canonicalize(
        {
            "bodyVersion": body_version,
            "chainId": chain_id,
            "chunkCount": chunk_count,
            "chunkIndex": chunk_index,
            "chunkPlaintextLength": chunk_plaintext_length,
            "domain": "EPOCH_AUTH_R3_BODY_CHUNK_V1",
            "formatVersion": 1,
            "manifestDigest": encode(manifest_digest),
            "plaintextLength": plaintext_length,
            "resourceId": resource_id,
        }
    )


class NonceUseRegistry:
    def __init__(self) -> None:
        self._used: set[tuple[bytes, bytes]] = set()

    def reserve(self, key: bytes, nonce_base: bytes) -> None:
        marker = (hashlib.sha256(key).digest(), bytes(nonce_base))
        if marker in self._used:
            raise NonceReuseError("CK/nonceBase reuse")
        self._used.add(marker)


def encrypt_chunk(key: bytes, nonce: bytes, plaintext: bytes, aad: bytes) -> bytes:
    return aes256_gcm_encrypt(key, nonce, plaintext, aad)


def decrypt_chunk(key: bytes, nonce: bytes, ciphertext: bytes, aad: bytes) -> bytes:
    return aes256_gcm_decrypt(key, nonce, ciphertext, aad)

