"""Standard Ed25519 and SHA-256 key helpers."""

from __future__ import annotations

from hashlib import sha256

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)


def generate_private_key() -> Ed25519PrivateKey:
    """Generate an Ed25519 private key for local prototype use."""

    return Ed25519PrivateKey.generate()


def public_key_bytes(key: Ed25519PublicKey) -> bytes:
    """Return the raw 32-byte Ed25519 public key."""

    return key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )


def user_key_id(public_key: bytes) -> bytes:
    """Return the SHA-256 fingerprint bound into a capability."""

    if not isinstance(public_key, bytes) or len(public_key) != 32:
        raise ValueError("Ed25519 public key must contain 32 bytes")
    return sha256(public_key).digest()


def sign(key: Ed25519PrivateKey, message: bytes) -> bytes:
    """Sign canonical CAP1 bytes with Ed25519."""

    return key.sign(message)


def verify(key: Ed25519PublicKey, signature: bytes, message: bytes) -> None:
    """Verify an Ed25519 signature, raising on failure."""

    key.verify(signature, message)
