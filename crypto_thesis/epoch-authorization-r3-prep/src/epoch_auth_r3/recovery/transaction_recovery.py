from __future__ import annotations

from dataclasses import dataclass

from .models import RecoveryDisposition


@dataclass(frozen=True)
class TransactionCandidate:
    tx_hash: str
    sender: str
    nonce: int
    target: str
    calldata_digest: str
    receipt_status: int | None
    operation_matches: bool


@dataclass(frozen=True)
class TransactionRecoveryResult:
    disposition: RecoveryDisposition
    tx_hash: str | None
    rebroadcast: bool = False


class CommitUnknownRecovery:
    def recover_known_hash(self, candidate: TransactionCandidate | None):
        if candidate is None:
            return TransactionRecoveryResult(RecoveryDisposition.RETRYABLE_TRANSIENT, None)
        if candidate.receipt_status == 1 and candidate.operation_matches:
            return TransactionRecoveryResult(RecoveryDisposition.AUTO_RECOVERABLE, candidate.tx_hash)
        if candidate.receipt_status == 0:
            return TransactionRecoveryResult(RecoveryDisposition.CONFLICT, candidate.tx_hash)
        return TransactionRecoveryResult(RecoveryDisposition.RETRYABLE_TRANSIENT, candidate.tx_hash)

    def recover_known_nonce(
        self, candidates: list[TransactionCandidate], *, sender: str, nonce: int,
        target: str, calldata_digest: str
    ):
        matches = [
            c for c in candidates
            if c.sender.lower() == sender.lower() and c.nonce == nonce
            and c.target.lower() == target.lower()
            and c.calldata_digest == calldata_digest and c.operation_matches
        ]
        if len(matches) == 1:
            return TransactionRecoveryResult(RecoveryDisposition.AUTO_RECOVERABLE, matches[0].tx_hash)
        return TransactionRecoveryResult(
            RecoveryDisposition.MANUAL_RECONCILIATION_REQUIRED, None
        )

    def recover_without_hash_or_nonce(self):
        return TransactionRecoveryResult(RecoveryDisposition.UNKNOWN_TRANSACTION, None)
