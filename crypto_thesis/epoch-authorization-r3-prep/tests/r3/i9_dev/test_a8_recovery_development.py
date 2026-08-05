from dataclasses import replace

from epoch_auth_r3.recovery import (
    FullReconcilerV1, RecoveryCoordinator, RecoveryDisposition,
    RecoverySnapshotV1, ResourceEvidence,
)
from scripts.r3_i9.run_p9a_development import (
    begin_repeatable_read_snapshot, development_state_payload,
)


def _snapshot():
    return RecoverySnapshotV1(
        "DEV_A8", 2026073005, 30, "ab" * 32,
        {"epoch": 1, "stateVersion": 1},
        {"headerVersion": 1, "bodyVersion": 1, "keyVersion": 1},
        {"status": "COMMITTED", "snapshotIdentity": "DEV_P9A"},
        ({"headerDigest": "11" * 32, "bodyDigest": "22" * 32},),
        (), (), ({"kind": "HEADER"}, {"kind": "BODY"}),
        ({"verified": True}, {"verified": True}),
        "AVAILABLE", "CURRENT", {"nextBlock": 31}, "2026-08-01T00:00:00Z",
    )


def test_recovery_snapshot_consistent_resource():
    assert RecoveryCoordinator(FullReconcilerV1()).reconcile_resource(ResourceEvidence("DEV_A8")).disposition is RecoveryDisposition.CONSISTENT


def test_recovery_fixed_chain_block():
    assert _snapshot().block_number == 30 and _snapshot().block_hash == "ab" * 32


def test_recovery_database_snapshot():
    assert _snapshot().database_job_state["snapshotIdentity"] == "DEV_P9A"


def test_recovery_consistent_no_write():
    result = FullReconcilerV1().classify(ResourceEvidence("DEV_A8"))
    assert result.automatic_actions == () and result.manual_reason is None


def test_recovery_consistent_no_object_restore():
    assert "RESTORE" not in " ".join(FullReconcilerV1().classify(ResourceEvidence("DEV_A8")).automatic_actions)


def test_recovery_consistent_material_release_allowed():
    assert FullReconcilerV1().classify(ResourceEvidence("DEV_A8")).material_release_allowed


def test_recovery_consistent_header_digest():
    assert _snapshot().header_version_state[0]["headerDigest"] == "11" * 32


def test_recovery_consistent_body_digest():
    assert _snapshot().header_version_state[0]["bodyDigest"] == "22" * 32


def test_recovery_database_snapshot_begins_after_factory_attestation_transaction():
    class Connection:
        def __init__(self): self.calls = []
        def commit(self): self.calls.append("COMMIT_ATTESTATION")
        def execute(self, sql): self.calls.append(sql)
    connection = Connection()
    begin_repeatable_read_snapshot(connection)
    assert connection.calls == [
        "COMMIT_ATTESTATION",
        "BEGIN ISOLATION LEVEL REPEATABLE READ READ ONLY",
    ]


def test_recovery_development_state_is_explicitly_namespaced():
    payload = development_state_payload("h", "b", "cid", "node")
    assert payload["developmentOnly"] is True
    assert payload["domain"] == "DEV_P9A"
    assert payload["encryptedCkRecord"]["present"] is True
    assert payload["recipientIndex"]["complete"] is True
    assert payload["storageReplica"]["verified"] is True
