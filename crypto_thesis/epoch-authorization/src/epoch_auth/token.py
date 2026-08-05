"""Signed capability construction and parsing helpers."""

from __future__ import annotations

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from .keys import sign
from .models import CapabilityPayload, SignedCapability
from .serialization import decode_capability, encode_capability


def sign_capability(
    payload: CapabilityPayload, private_key: Ed25519PrivateKey
) -> SignedCapability:
    """Canonicalize and sign a CAP1 payload."""

    encoded = encode_capability(payload)
    return SignedCapability(payload, encoded, sign(private_key, encoded))


def parse_signed_capability(payload_bytes: bytes, signature: bytes) -> SignedCapability:
    """Decode a wire capability while retaining its exact signed bytes."""

    payload = decode_capability(payload_bytes)
    return SignedCapability(payload, payload_bytes, signature)
