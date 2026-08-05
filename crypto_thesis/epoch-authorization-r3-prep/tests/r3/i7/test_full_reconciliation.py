import pytest

from epoch_auth_r3.recovery import FullReconcilerV1, RecoveryCoordinator, RecoveryDisposition, ResourceEvidence


@pytest.mark.parametrize(
    ("changes", "expected"),
    [
        ({}, RecoveryDisposition.CONSISTENT),
        ({"chain_available": False}, RecoveryDisposition.FAIL_CLOSED_CHAIN_UNAVAILABLE),
        ({"database_available": False}, RecoveryDisposition.FAIL_CLOSED_DATABASE_UNAVAILABLE),
        ({"authorization_matches_header": False}, RecoveryDisposition.AUTO_RECOVERABLE),
        ({"chain_anchor_exists": False}, RecoveryDisposition.CONFLICT),
        ({"database_committed": False}, RecoveryDisposition.AUTO_RECOVERABLE),
        ({"header_object_exists": False}, RecoveryDisposition.IRRECOVERABLE_CONTENT_LOSS),
        ({"body_object_exists": False}, RecoveryDisposition.IRRECOVERABLE_CONTENT_LOSS),
        ({"header_digest_matches": False}, RecoveryDisposition.FAIL_CLOSED_CORRUPT_OBJECT),
        ({"body_digest_matches": False}, RecoveryDisposition.FAIL_CLOSED_CORRUPT_OBJECT),
        ({"recipient_index_matches": False}, RecoveryDisposition.AUTO_RECOVERABLE),
    ],
)
def test_reconciliation_classification(changes, expected):
    evidence = ResourceEvidence("r", **changes)
    assert FullReconcilerV1().classify(evidence).disposition == expected


def test_chain_ahead_database_does_not_release_until_reconciled():
    result = RecoveryCoordinator(FullReconcilerV1()).reconcile_resource(
        ResourceEvidence("r", database_committed=False)
    )
    assert not result.material_release_allowed


def test_consistent_state_enables_release():
    coordinator = RecoveryCoordinator(FullReconcilerV1())
    coordinator.reconcile_resource(ResourceEvidence("r"))
    assert coordinator.material_release_enabled


def test_bounded_reconciliation_rejects_unbounded_input():
    with pytest.raises(ValueError):
        FullReconcilerV1().reconcile_all_bounded(
            [ResourceEvidence(str(i)) for i in range(3)], limit=2
        )


def test_object_ahead_is_orphaned():
    result = FullReconcilerV1().classify(
        ResourceEvidence("r", chain_anchor_exists=False, database_committed=False,
                         database_candidate_exists=True)
    )
    assert result.disposition == RecoveryDisposition.ORPHANED_OBJECT


def test_old_object_ahead_is_superseded():
    result = FullReconcilerV1().classify(
        ResourceEvidence("r", chain_anchor_exists=False, database_committed=False,
                         database_candidate_exists=True, newer_state_exists=True)
    )
    assert result.disposition == RecoveryDisposition.SUPERSEDED
