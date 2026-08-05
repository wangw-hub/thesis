"""Domain-specific exceptions for time-policy compilation."""


class TimePolicyError(ValueError):
    """Base class for invalid time-policy input."""


class TimezoneRequiredError(TimePolicyError):
    """Raised when a datetime has no usable timezone."""


class InvalidIntervalError(TimePolicyError):
    """Raised when an interval is empty, reversed, or outside the domain."""


class SerializationError(TimePolicyError):
    """Raised when canonical encoding or decoding fails."""
