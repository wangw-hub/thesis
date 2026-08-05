from __future__ import annotations

import hashlib
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from epoch_auth_r3.serialization.jcs_adapter import canonicalize


class RecoveryDisposition(StrEnum):
    CONSISTENT = "CONSISTENT"
    AUTO_RECOVERABLE = "AUTO_RECOVERABLE"
    RETRYABLE_TRANSIENT = "RETRYABLE_TRANSIENT"
    MANUAL_RECONCILIATION_REQUIRED = "MANUAL_RECONCILIATION_REQUIRED"
    FAIL_CLOSED_MISSING_OBJECT = "FAIL_CLOSED_MISSING_OBJECT"
    FAIL_CLOSED_CORRUPT_OBJECT = "FAIL_CLOSED_CORRUPT_OBJECT"
    FAIL_CLOSED_KEY_UNAVAILABLE = "FAIL_CLOSED_KEY_UNAVAILABLE"
    FAIL_CLOSED_CHAIN_UNAVAILABLE = "FAIL_CLOSED_CHAIN_UNAVAILABLE"
    FAIL_CLOSED_DATABASE_UNAVAILABLE = "FAIL_CLOSED_DATABASE_UNAVAILABLE"
    IRRECOVERABLE_CONTENT_LOSS = "IRRECOVERABLE_CONTENT_LOSS"
    IRRECOVERABLE_KEY_LOSS = "IRRECOVERABLE_KEY_LOSS"
    SUPERSEDED = "SUPERSEDED"
    ORPHANED_OBJECT = "ORPHANED_OBJECT"
    ORPHANED_DATABASE_RECORD = "ORPHANED_DATABASE_RECORD"
    UNKNOWN_TRANSACTION = "UNKNOWN_TRANSACTION"
    CONFLICT = "CONFLICT"
    UNSUPPORTED = "UNSUPPORTED"


@dataclass(frozen=True)
class RecoverySnapshotV1:
    snapshot_id: str
    chain_id: int
    block_number: int
    block_hash: str
    authorization_state: dict[str, Any]
    header_registry_state: dict[str, Any]
    database_job_state: dict[str, Any]
    header_version_state: tuple[dict[str, Any], ...]
    commit_attempts: tuple[dict[str, Any], ...]
    authorization_events: tuple[dict[str, Any], ...]
    object_references: tuple[dict[str, Any], ...]
    object_verification_results: tuple[dict[str, Any], ...]
    content_key_record_status: str
    recipient_index_status: str
    cursor_state: dict[str, Any]
    captured_at: str

    def canonical_dict(self) -> dict[str, Any]:
        return {
            "authorizationEvents": self.authorization_events,
            "authorizationState": self.authorization_state,
            "blockHash": self.block_hash,
            "blockNumber": self.block_number,
            "chainId": self.chain_id,
            "commitAttempts": self.commit_attempts,
            "contentKeyRecordStatus": self.content_key_record_status,
            "cursorState": self.cursor_state,
            "databaseJobState": self.database_job_state,
            "headerRegistryState": self.header_registry_state,
            "headerVersionState": self.header_version_state,
            "objectReferences": self.object_references,
            "objectVerificationResults": self.object_verification_results,
            "recipientIndexStatus": self.recipient_index_status,
            "snapshotId": self.snapshot_id,
        }

    @property
    def snapshot_digest(self) -> str:
        # capturedAt is audit metadata, not state identity.
        return hashlib.sha256(canonicalize(self.canonical_dict())).hexdigest()


@dataclass(frozen=True)
class ResourceRecoveryResult:
    resource_id: str
    disposition: RecoveryDisposition
    material_release_allowed: bool
    automatic_actions: tuple[str, ...] = ()
    manual_reason: str | None = None
