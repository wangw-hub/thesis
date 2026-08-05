from __future__ import annotations

from dataclasses import dataclass, replace

from epoch_auth_r3.crypto.exceptions import CryptoValidationError, IntegrityError
from epoch_auth_r3.crypto.key_material import require_length

from .chunk_crypto import (
    NonceUseRegistry,
    chunk_aad,
    chunk_nonce,
    decrypt_chunk,
    encrypt_chunk,
)
from .manifest import manifest_digest


@dataclass(frozen=True)
class EncryptedChunk:
    index: int
    plaintext_length: int
    ciphertext: bytes


@dataclass(frozen=True)
class BodyEnvelopeV1:
    format_version: int
    chain_id: int
    resource_id: str
    body_version: int
    nonce_base: bytes
    chunk_size: int
    plaintext_length: int
    chunk_count: int
    manifest_digest: bytes
    chunks: tuple[EncryptedChunk, ...]


def _split(plaintext: bytes, chunk_size: int) -> list[bytes]:
    if chunk_size <= 0:
        raise CryptoValidationError("chunk_size must be positive")
    if not plaintext:
        return [b""]
    return [plaintext[i : i + chunk_size] for i in range(0, len(plaintext), chunk_size)]


def encrypt_body(
    *,
    plaintext: bytes,
    ck: bytes,
    nonce_base: bytes,
    chain_id: int,
    resource_id: str,
    body_version: int,
    chunk_size: int,
    nonce_registry: NonceUseRegistry,
) -> BodyEnvelopeV1:
    require_length(ck, 32, "CK")
    require_length(nonce_base, 8, "nonceBase")
    nonce_registry.reserve(ck, nonce_base)
    parts = _split(bytes(plaintext), chunk_size)
    lengths = [len(part) for part in parts]
    digest = manifest_digest(
        chain_id=chain_id,
        resource_id=resource_id,
        body_version=body_version,
        plaintext_length=len(plaintext),
        chunk_lengths=lengths,
    )
    chunks = []
    for index, part in enumerate(parts):
        aad = chunk_aad(
            chain_id=chain_id,
            resource_id=resource_id,
            body_version=body_version,
            manifest_digest=digest,
            chunk_index=index,
            chunk_count=len(parts),
            plaintext_length=len(plaintext),
            chunk_plaintext_length=len(part),
        )
        chunks.append(
            EncryptedChunk(
                index,
                len(part),
                encrypt_chunk(ck, chunk_nonce(nonce_base, index), part, aad),
            )
        )
    return BodyEnvelopeV1(
        1,
        chain_id,
        resource_id,
        body_version,
        nonce_base,
        chunk_size,
        len(plaintext),
        len(chunks),
        digest,
        tuple(chunks),
    )


def decrypt_body(envelope: BodyEnvelopeV1, ck: bytes) -> bytes:
    require_length(ck, 32, "CK")
    if envelope.format_version != 1:
        raise CryptoValidationError("unsupported Body format")
    if envelope.chunk_count != len(envelope.chunks) or envelope.chunk_count < 1:
        raise IntegrityError("chunk count mismatch")
    indices = [item.index for item in envelope.chunks]
    if indices != list(range(envelope.chunk_count)):
        raise IntegrityError("chunk order, deletion, or duplication detected")
    lengths = [item.plaintext_length for item in envelope.chunks]
    expected_manifest = manifest_digest(
        chain_id=envelope.chain_id,
        resource_id=envelope.resource_id,
        body_version=envelope.body_version,
        plaintext_length=envelope.plaintext_length,
        chunk_lengths=lengths,
    )
    if expected_manifest != envelope.manifest_digest:
        raise IntegrityError("manifest mismatch")
    recovered: list[bytes] = []
    for item in envelope.chunks:
        aad = chunk_aad(
            chain_id=envelope.chain_id,
            resource_id=envelope.resource_id,
            body_version=envelope.body_version,
            manifest_digest=envelope.manifest_digest,
            chunk_index=item.index,
            chunk_count=envelope.chunk_count,
            plaintext_length=envelope.plaintext_length,
            chunk_plaintext_length=item.plaintext_length,
        )
        part = decrypt_chunk(
            ck,
            chunk_nonce(envelope.nonce_base, item.index),
            item.ciphertext,
            aad,
        )
        if len(part) != item.plaintext_length:
            raise IntegrityError("chunk plaintext length mismatch")
        recovered.append(part)
    plaintext = b"".join(recovered)
    if len(plaintext) != envelope.plaintext_length:
        raise IntegrityError("file truncation or append detected")
    return plaintext


def altered(envelope: BodyEnvelopeV1, **changes) -> BodyEnvelopeV1:
    """Test helper for immutable project vectors."""
    return replace(envelope, **changes)

