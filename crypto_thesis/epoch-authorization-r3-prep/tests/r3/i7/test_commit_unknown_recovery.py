from epoch_auth_r3.recovery.models import RecoveryDisposition
from epoch_auth_r3.recovery.transaction_recovery import (
    CommitUnknownRecovery,
    TransactionCandidate,
)


def _candidate(**changes):
    values = dict(tx_hash="0x1", sender="0xabc", nonce=4, target="0xdef",
                  calldata_digest="12" * 32, receipt_status=1, operation_matches=True)
    values.update(changes)
    return TransactionCandidate(**values)


def test_known_hash_confirmed_recovers_without_rebroadcast():
    result = CommitUnknownRecovery().recover_known_hash(_candidate())
    assert result.disposition == RecoveryDisposition.AUTO_RECOVERABLE
    assert result.rebroadcast is False


def test_known_hash_revert_is_conflict():
    assert CommitUnknownRecovery().recover_known_hash(
        _candidate(receipt_status=0)
    ).disposition == RecoveryDisposition.CONFLICT


def test_known_hash_pending_is_retryable():
    assert CommitUnknownRecovery().recover_known_hash(
        _candidate(receipt_status=None)
    ).disposition == RecoveryDisposition.RETRYABLE_TRANSIENT


def test_known_nonce_unique_match():
    c = _candidate()
    result = CommitUnknownRecovery().recover_known_nonce(
        [c], sender=c.sender, nonce=c.nonce, target=c.target,
        calldata_digest=c.calldata_digest,
    )
    assert result.tx_hash == c.tx_hash and not result.rebroadcast


def test_known_nonce_ambiguous_requires_manual():
    c = _candidate()
    result = CommitUnknownRecovery().recover_known_nonce(
        [c, c], sender=c.sender, nonce=c.nonce, target=c.target,
        calldata_digest=c.calldata_digest,
    )
    assert result.disposition == RecoveryDisposition.MANUAL_RECONCILIATION_REQUIRED


def test_no_hash_or_nonce_never_rebroadcasts():
    result = CommitUnknownRecovery().recover_without_hash_or_nonce()
    assert result.disposition == RecoveryDisposition.UNKNOWN_TRANSACTION
    assert not result.rebroadcast
