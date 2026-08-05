from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from epoch_auth_r3.storage.references import ObjectKind, validate_digest

from .cid import parse_cid_v1
from .exceptions import ReplicaVerificationError


class ReplicationStatus(StrEnum):
    PENDING = "PENDING"
    ADDING = "ADDING"
    ADDED = "ADDED"
    READBACK_VERIFIED = "READBACK_VERIFIED"
    PINNED = "PINNED"
    FAILED = "FAILED"
    MISSING = "MISSING"
    CORRUPT = "CORRUPT"
    SUPERSEDED = "SUPERSEDED"


class VerificationStatus(StrEnum):
    UNVERIFIED = "UNVERIFIED"
    DIGEST_VERIFIED = "DIGEST_VERIFIED"
    OBJECT_VERIFIED = "OBJECT_VERIFIED"
    FAILED = "FAILED"


@dataclass(frozen=True)
class StorageReplicaRecordV1:
    schema_version: int
    object_digest_algorithm: str
    object_digest_hex: str
    object_size_bytes: int
    object_kind: ObjectKind
    replica_backend: str
    cid: str
    cid_version: int
    multihash_code: int
    codec: int
    chunker_profile: str
    pin_status: bool
    replication_status: ReplicationStatus
    verification_status: VerificationStatus
    kubo_node_id: str

    def __post_init__(self):
        parsed = parse_cid_v1(self.cid)
        if self.schema_version != 1 or self.object_digest_algorithm != "sha256":
            raise ReplicaVerificationError("UNSUPPORTED_REPLICA_SCHEMA")
        validate_digest(self.object_digest_hex)
        if type(self.object_size_bytes) is not int or self.object_size_bytes < 0:
            raise ReplicaVerificationError("INVALID_REPLICA_SIZE")
        if self.replica_backend != "IPFS_KUBO":
            raise ReplicaVerificationError("UNSUPPORTED_REPLICA_BACKEND")
        if (self.cid_version, self.multihash_code, self.codec) != (
            parsed.version, parsed.multihash_code, parsed.codec
        ):
            raise ReplicaVerificationError("CID_METADATA_MISMATCH")
        if self.pin_status and self.replication_status != ReplicationStatus.PINNED:
            raise ReplicaVerificationError("PIN_STATUS_MISMATCH")
        if self.replication_status == ReplicationStatus.PINNED and (
            not self.pin_status or self.verification_status != VerificationStatus.OBJECT_VERIFIED
        ):
            raise ReplicaVerificationError("UNVERIFIED_PIN")


@dataclass(frozen=True)
class ReplicaVerificationResultV1:
    verified: bool
    digest_matches: bool
    size_matches: bool
    object_valid: bool
    error_code: str | None = None
