from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)

from .exceptions import CryptoValidationError, IntegrityError
from .key_material import require_length


HEADER_DOMAIN = b"EPOCH_AUTH_R3_HEADER_V1"
CAP2_DOMAIN = b"EPOCH_AUTH_CAP2_V2"


def _lp(value: bytes) -> bytes:
    if len(value) > 65535:
        raise CryptoValidationError("field too long")
    return len(value).to_bytes(2, "big") + value


def header_signature_input(
    *,
    chain_id: int,
    authorization_contract: bytes,
    header_registry: bytes,
    header_digest: bytes,
    issuer_key_id: str,
    domain: bytes = HEADER_DOMAIN,
) -> bytes:
    if not 0 <= chain_id < 2**64:
        raise CryptoValidationError("chain_id out of uint64 range")
    return b"".join(
        (
            _lp(domain),
            chain_id.to_bytes(8, "big"),
            require_length(authorization_contract, 20, "authorization contract"),
            require_length(header_registry, 20, "header registry"),
            require_length(header_digest, 32, "header digest"),
            _lp(issuer_key_id.encode("utf-8")),
        )
    )


def sign_header(private_seed: bytes, **context) -> bytes:
    return Ed25519PrivateKey.from_private_bytes(
        require_length(private_seed, 32, "Ed25519 private seed")
    ).sign(header_signature_input(**context))


def verify_header(public_key: bytes, signature: bytes, **context) -> None:
    require_length(signature, 64, "Ed25519 signature")
    try:
        Ed25519PublicKey.from_public_bytes(
            require_length(public_key, 32, "Ed25519 public key")
        ).verify(signature, header_signature_input(**context))
    except (InvalidSignature, ValueError) as exc:
        raise IntegrityError("HEADER_SIGNATURE_INVALID") from exc

