import base64
import re

from epoch_auth_r3.crypto.exceptions import CryptoValidationError


_B64URL = re.compile(r"^[A-Za-z0-9_-]*$")


def encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def decode(value: str) -> bytes:
    if not isinstance(value, str) or "=" in value or not _B64URL.fullmatch(value):
        raise CryptoValidationError("invalid unpadded base64url")
    try:
        raw = base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))
    except Exception as exc:
        raise CryptoValidationError("invalid base64url") from exc
    if encode(raw) != value:
        raise CryptoValidationError("non-canonical base64url")
    return raw

