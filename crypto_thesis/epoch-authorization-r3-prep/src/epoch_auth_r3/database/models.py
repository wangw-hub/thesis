from dataclasses import dataclass
from enum import StrEnum


class JobStatus(StrEnum):
    PENDING = "PENDING"
    CLAIMED = "CLAIMED"
    CANDIDATE_STORED = "CANDIDATE_STORED"
    READY_FOR_CHAIN_COMMIT = "READY_FOR_CHAIN_COMMIT"
    COMMIT_UNKNOWN = "COMMIT_UNKNOWN"
    COMMITTED = "COMMITTED"
    RETRY_WAIT = "RETRY_WAIT"
    FAILED_TERMINAL = "FAILED_TERMINAL"
    DEAD_LETTER = "DEAD_LETTER"


class InsertResult(StrEnum):
    CREATED = "CREATED"
    EXISTING_IDENTICAL = "EXISTING_IDENTICAL"
    CONFLICTING_DUPLICATE = "CONFLICTING_DUPLICATE"


@dataclass(frozen=True)
class SyntheticRevocationEventV1:
    chain_id: int
    authorization_contract: bytes
    header_registry: bytes
    event_signature: bytes
    tx_hash: bytes
    log_index: int
    block_number: int
    block_hash: bytes
    resource_id: bytes
    new_epoch: int
    new_state_version: int
    new_header_version: int
    new_key_version: int

    def __post_init__(self) -> None:
        if not 0 <= self.chain_id < 2**63:
            raise ValueError("chain_id out of range")
        for name in ("authorization_contract", "header_registry"):
            if len(getattr(self, name)) != 20:
                raise ValueError(f"{name} must be 20 bytes")
        for name in ("event_signature", "tx_hash", "block_hash", "resource_id"):
            if len(getattr(self, name)) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        for name in ("log_index", "block_number", "new_epoch", "new_state_version"):
            if not 0 <= getattr(self, name) < 2**63:
                raise ValueError(f"{name} out of range")
        for name in ("new_header_version", "new_key_version"):
            if not 0 < getattr(self, name) < 2**63:
                raise ValueError(f"{name} out of range")
