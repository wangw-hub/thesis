from __future__ import annotations

from dataclasses import dataclass

from .exceptions import CryptoValidationError


@dataclass(frozen=True)
class TestOnlyEphemeral:
    """RFC/project-vector material; forbidden on the production seal path."""

    private_key: bytes
    public_key: bytes

    def __post_init__(self) -> None:
        if len(self.private_key) != 32 or len(self.public_key) != 32:
            raise CryptoValidationError("X25519 test keys must be 32 bytes")


def require_length(value: bytes, length: int, label: str) -> bytes:
    if not isinstance(value, bytes) or len(value) != length:
        raise CryptoValidationError(f"{label} must be {length} bytes")
    return value

