from epoch_auth_r3.recovery import DatabaseDerivedStateRebuilder
from epoch_auth_r3.recovery.key_recovery import classify_key_recovery
from epoch_auth_r3.recovery.models import RecoveryDisposition
from epoch_auth_r3.recovery.index_rebuilder import RecipientIndexRebuilder


def test_transient_key_unavailable_fails_closed():
    assert classify_key_recovery(available=False) == RecoveryDisposition.FAIL_CLOSED_KEY_UNAVAILABLE


def test_permanent_key_loss_is_irrecoverable():
    assert classify_key_recovery(
        available=False, permanent_loss=True
    ) == RecoveryDisposition.IRRECOVERABLE_KEY_LOSS


def test_available_key_is_consistent():
    assert classify_key_recovery(available=True) == RecoveryDisposition.CONSISTENT


def test_derived_rebuild_marks_history_incomplete():
    result = DatabaseDerivedStateRebuilder().rebuild(
        chain_anchor_verified=True, header_object_verified=True
    )
    assert result.label == "DERIVED_RECOVERY_STATE"
    assert result.current_state_rebuilt and not result.history_complete


def test_derived_rebuild_requires_verified_object():
    result = DatabaseDerivedStateRebuilder().rebuild(
        chain_anchor_verified=True, header_object_verified=False
    )
    assert result.disposition == RecoveryDisposition.FAIL_CLOSED_MISSING_OBJECT


def test_index_rebuild_requires_external_anchor_and_verified_header():
    assert not RecipientIndexRebuilder().rebuild(
        anchor_matches=False, header_verified=True, recipients=[]
    ).complete


def test_index_rebuild_is_deterministic():
    recipients = [
        {"userId": "b", "recipientKeyId": "k2", "userVersion": 2},
        {"userId": "a", "recipientKeyId": "k1", "userVersion": 1},
    ]
    result = RecipientIndexRebuilder().rebuild(
        anchor_matches=True, header_verified=True, recipients=recipients
    )
    assert result.complete and result.entries[0][0] == "a"
