import re

from epoch_auth_r3.crypto.exceptions import CryptoValidationError


_ADDRESS = re.compile(r"^0x[0-9a-f]{40}$")
_HEX32 = re.compile(r"^[0-9a-f]{64}$")


def normalize_address(value: str) -> str:
    if not isinstance(value, str):
        raise CryptoValidationError("address must be text")
    normalized = value.lower()
    if not _ADDRESS.fullmatch(normalized):
        raise CryptoValidationError("address must be 20-byte lowercase hex")
    return normalized


def normalize_hex32(value: str) -> str:
    if not isinstance(value, str):
        raise CryptoValidationError("digest must be text")
    normalized = value.lower()
    if not _HEX32.fullmatch(normalized):
        raise CryptoValidationError("digest must be 32-byte lowercase hex")
    return normalized


def require_safe_integer(value: int, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise CryptoValidationError(f"{label} must be an integer")
    if not 0 <= value <= 2**53 - 1:
        raise CryptoValidationError(f"{label} outside I-JSON safe range")
    return value

