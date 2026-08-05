from __future__ import annotations

from dataclasses import dataclass

from .models import RecoveryDisposition, ResourceRecoveryResult


@dataclass(frozen=True)
class ResourceEvidence:
    resource_id: str
    chain_available: bool = True
    database_available: bool = True
    authorization_matches_header: bool = True
    chain_anchor_exists: bool = True
    database_committed: bool = True
    database_candidate_exists: bool = False
    header_object_exists: bool = True
    header_digest_matches: bool = True
    body_object_exists: bool = True
    body_digest_matches: bool = True
    recipient_index_matches: bool = True
    trusted_header_backup: bool = False
    trusted_body_backup: bool = False
    newer_state_exists: bool = False


class FullReconcilerV1:
    def classify(self, e: ResourceEvidence) -> ResourceRecoveryResult:
        deny = lambda d, reason=None, actions=(): ResourceRecoveryResult(
            e.resource_id, d, False, tuple(actions), reason
        )
        if not e.chain_available:
            return deny(RecoveryDisposition.FAIL_CLOSED_CHAIN_UNAVAILABLE)
        if not e.database_available:
            return deny(RecoveryDisposition.FAIL_CLOSED_DATABASE_UNAVAILABLE)
        if not e.authorization_matches_header:
            return deny(
                RecoveryDisposition.AUTO_RECOVERABLE,
                "HEADER_UPDATE_PENDING",
                ("ENSURE_CURRENT_EVENT_AND_JOB",),
            )
        if e.database_committed and not e.chain_anchor_exists:
            return deny(
                RecoveryDisposition.CONFLICT,
                "DATABASE_AHEAD_OF_CHAIN",
            )
        if e.chain_anchor_exists and not e.database_committed:
            return deny(
                RecoveryDisposition.AUTO_RECOVERABLE,
                "CHAIN_AHEAD_OF_DATABASE",
                ("VERIFY_RECEIPT_AND_OBJECTS", "CAS_DATABASE_FORWARD", "APPEND_RECOVERY_AUDIT"),
            )
        if e.database_candidate_exists and not e.chain_anchor_exists:
            if e.newer_state_exists:
                return deny(RecoveryDisposition.SUPERSEDED, "OBJECT_AHEAD_SUPERSEDED")
            return deny(RecoveryDisposition.ORPHANED_OBJECT, "OBJECT_AHEAD_OF_CHAIN")
        if e.chain_anchor_exists and (not e.header_object_exists or not e.body_object_exists):
            if (not e.header_object_exists and e.trusted_header_backup) or (
                not e.body_object_exists and e.trusted_body_backup
            ):
                return deny(
                    RecoveryDisposition.AUTO_RECOVERABLE,
                    "TRUSTED_BACKUP_AVAILABLE",
                    ("RESTORE_AND_VERIFY_OBJECT",),
                )
            return deny(
                RecoveryDisposition.IRRECOVERABLE_CONTENT_LOSS,
                "CHAIN_ANCHOR_OBJECT_MISSING",
            )
        if not e.header_digest_matches or not e.body_digest_matches:
            return deny(RecoveryDisposition.FAIL_CLOSED_CORRUPT_OBJECT, "OBJECT_DIGEST_MISMATCH")
        if not e.recipient_index_matches:
            return deny(
                RecoveryDisposition.AUTO_RECOVERABLE,
                "RECIPIENT_INDEX_REBUILD",
                ("REBUILD_FROM_VERIFIED_CURRENT_HEADER",),
            )
        return ResourceRecoveryResult(
            e.resource_id, RecoveryDisposition.CONSISTENT, True
        )

    def reconcile_all_bounded(
        self, resources: list[ResourceEvidence], *, limit: int = 100
    ) -> tuple[ResourceRecoveryResult, ...]:
        if len(resources) > limit:
            raise ValueError("bounded reconciliation limit exceeded")
        return tuple(self.classify(item) for item in resources)
