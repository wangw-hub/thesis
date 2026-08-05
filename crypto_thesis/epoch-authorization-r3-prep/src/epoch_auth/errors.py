"""Protocol errors and deterministic rejection codes."""

from __future__ import annotations

from enum import StrEnum


class RejectCode(StrEnum):
    """Frozen verification and issuance rejection codes."""

    INVALID_SIGNATURE = "INVALID_SIGNATURE"
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    RESOURCE_INACTIVE = "RESOURCE_INACTIVE"
    USER_NOT_FOUND = "USER_NOT_FOUND"
    USER_INACTIVE = "USER_INACTIVE"
    POLICY_DIGEST_MISMATCH = "POLICY_DIGEST_MISMATCH"
    EPOCH_MISMATCH = "EPOCH_MISMATCH"
    USER_KEY_MISMATCH = "USER_KEY_MISMATCH"
    NOT_YET_VALID = "NOT_YET_VALID"
    EXPIRED = "EXPIRED"
    TIME_POLICY_DENIED = "TIME_POLICY_DENIED"
    NONCE_REPLAY = "NONCE_REPLAY"
    OPERATION_MISMATCH = "OPERATION_MISMATCH"
    CHAIN_CONTEXT_MISMATCH = "CHAIN_CONTEXT_MISMATCH"
    STATE_VERSION_MISMATCH = "STATE_VERSION_MISMATCH"
    USER_VERSION_MISMATCH = "USER_VERSION_MISMATCH"
    SYSTEM_STATE_UNAVAILABLE = "SYSTEM_STATE_UNAVAILABLE"
    MALFORMED_TOKEN = "MALFORMED_TOKEN"


class ProtocolError(ValueError):
    """Base exception for malformed protocol inputs."""


class StateTransitionError(ProtocolError):
    """Raised when a state transition is invalid."""


class TokenDecodeError(ProtocolError):
    """Raised when CAP1 bytes are malformed or non-canonical."""
