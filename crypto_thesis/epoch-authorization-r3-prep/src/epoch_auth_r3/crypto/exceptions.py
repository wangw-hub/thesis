class CryptoValidationError(ValueError):
    """Fail-closed validation failure."""


class IntegrityError(CryptoValidationError):
    """Authenticated data failed validation."""


class NonceReuseError(CryptoValidationError):
    """A key/nonce space was reused."""

