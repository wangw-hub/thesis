"""Immutable protocol data models."""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum, StrEnum

from .errors import RejectCode

UINT64_MAX = (1 << 64) - 1


def _nonempty_text(name: str, value: str) -> None:
    if not isinstance(value, str) or not value or len(value.encode("utf-8")) > 65535:
        raise ValueError(f"{name} must be non-empty UTF-8 text of at most 65535 bytes")


def _uint64(name: str, value: int) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= UINT64_MAX:
        raise ValueError(f"{name} must be an unsigned 64-bit integer")


def _bytes_len(name: str, value: bytes, length: int) -> None:
    if not isinstance(value, bytes) or len(value) != length:
        raise ValueError(f"{name} must contain {length} bytes")


class ResourceStatus(StrEnum):
    """Lifecycle state of a registered resource."""

    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    REVOKED = "REVOKED"


class UserStatus(StrEnum):
    """Lifecycle state of a registered user."""

    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    REVOKED = "REVOKED"


class Operation(IntEnum):
    """Capability operation identifiers."""

    READ = 1
    UPDATE = 2
    MANAGE = 3


@dataclass(frozen=True, slots=True)
class ResourceState:
    """Confirmed authorization state for one resource."""

    resource_id: str
    owner_id: str
    policy_digest: bytes
    epoch: int
    status: ResourceStatus
    updated_version: int

    def __post_init__(self) -> None:
        _nonempty_text("resource_id", self.resource_id)
        _nonempty_text("owner_id", self.owner_id)
        _bytes_len("policy_digest", self.policy_digest, 32)
        _uint64("epoch", self.epoch)
        _uint64("updated_version", self.updated_version)


@dataclass(frozen=True, slots=True)
class UserState:
    """Registered user and bound public-key fingerprint."""

    user_id: str
    user_key_id: bytes
    status: UserStatus
    user_version: int = 1

    def __post_init__(self) -> None:
        _nonempty_text("user_id", self.user_id)
        _bytes_len("user_key_id", self.user_key_id, 32)
        _uint64("user_version", self.user_version)
        if self.user_version == 0:
            raise ValueError("user_version must be positive")


@dataclass(frozen=True, slots=True)
class AuthorizationRequest:
    """Request context supplied to the capability issuer."""

    resource_id: str
    user_id: str
    user_public_key: bytes
    operation: Operation
    now: int
    ttl: int
    nonce: bytes

    def __post_init__(self) -> None:
        _nonempty_text("resource_id", self.resource_id)
        _nonempty_text("user_id", self.user_id)
        _bytes_len("user_public_key", self.user_public_key, 32)
        _uint64("now", self.now)
        if isinstance(self.ttl, bool) or not isinstance(self.ttl, int) or self.ttl <= 0:
            raise ValueError("ttl must be a positive integer")
        _bytes_len("nonce", self.nonce, 16)


@dataclass(frozen=True, slots=True)
class MatchedNode:
    """Dyadic node consumed by Proposed-C for one authorization decision."""

    start: int
    size: int

    def __post_init__(self) -> None:
        _uint64("start", self.start)
        _uint64("size", self.size)
        if self.size == 0 or self.size & (self.size - 1) or self.start % self.size:
            raise ValueError("matched node must be aligned and power-of-two sized")


@dataclass(frozen=True, slots=True)
class ChainBinding:
    """CAP2 binding to one chain, contract, and confirmed state versions."""

    chain_id: int
    contract_address: bytes
    resource_state_version: int
    user_version: int

    def __post_init__(self) -> None:
        _uint64("chain_id", self.chain_id)
        if self.chain_id == 0:
            raise ValueError("chain_id must be positive")
        _bytes_len("contract_address", self.contract_address, 20)
        _uint64("resource_state_version", self.resource_state_version)
        _uint64("user_version", self.user_version)
        if self.resource_state_version == 0 or self.user_version == 0:
            raise ValueError("state versions must be positive")


@dataclass(frozen=True, slots=True)
class CapabilityPayload:
    """Signed CAP1 payload."""

    version: int
    issuer: str
    resource_id: str
    policy_digest: bytes
    epoch: int
    user_key_id: bytes
    operation: Operation
    not_before: int
    expires_at: int
    nonce: bytes
    issued_at: int
    chain_binding: ChainBinding | None = None
    matched_node: MatchedNode | None = None
    cover_version: bytes | None = None

    def __post_init__(self) -> None:
        if self.version not in (1, 2):
            raise ValueError("capability version must be 1 or 2")
        _nonempty_text("issuer", self.issuer)
        _nonempty_text("resource_id", self.resource_id)
        _bytes_len("policy_digest", self.policy_digest, 32)
        _uint64("epoch", self.epoch)
        _bytes_len("user_key_id", self.user_key_id, 32)
        _uint64("not_before", self.not_before)
        _uint64("expires_at", self.expires_at)
        _uint64("issued_at", self.issued_at)
        if not self.not_before <= self.issued_at < self.expires_at:
            raise ValueError("CAP1 time bounds must contain issued_at")
        _bytes_len("nonce", self.nonce, 16)
        if (self.version == 1) != (self.chain_binding is None):
            raise ValueError("CAP1 omits and CAP2 requires chain_binding")
        if (self.matched_node is None) != (self.cover_version is None):
            raise ValueError("matched_node and cover_version must appear together")
        if self.cover_version is not None:
            _bytes_len("cover_version", self.cover_version, 32)


@dataclass(frozen=True, slots=True)
class SignedCapability:
    """Canonical payload bytes with an Ed25519 signature."""

    payload: CapabilityPayload
    payload_bytes: bytes
    signature: bytes

    def __post_init__(self) -> None:
        _bytes_len("signature", self.signature, 64)


@dataclass(frozen=True, slots=True)
class AuthorizationDecision:
    """Deterministic authorization result."""

    accepted: bool
    code: RejectCode | None
    capability: SignedCapability | None = None

    def __post_init__(self) -> None:
        if self.accepted != (self.code is None):
            raise ValueError("accepted decisions cannot have a rejection code")
        if not self.accepted and self.capability is not None:
            raise ValueError("rejected decisions cannot carry a capability")
