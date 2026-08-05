from dataclasses import replace

import pytest

from epoch_auth_r3.recovery import RecoveryAuthority, RecoveryAuthorityMatrixV1, RecoverySnapshotV1


def _snapshot(captured_at="2026-07-30T00:00:00Z"):
    return RecoverySnapshotV1(
        "snap", 7, 11, "0x" + "12" * 32,
        {"epoch": 2}, {"headerVersion": 3}, {"status": "COMMITTED"},
        ({"headerVersion": 3},), (), (), (), (), "AVAILABLE", "CURRENT",
        {"nextBlock": 12}, captured_at,
    )


@pytest.mark.parametrize(
    ("field", "authority"),
    [
        ("epoch", RecoveryAuthority.AUTHORIZATION_STATE),
        ("currentKeyVersion", RecoveryAuthority.HEADER_REGISTRY),
        ("signedHeaderBytes", RecoveryAuthority.LOCAL_OBJECT_STORE),
        ("workflow", RecoveryAuthority.POSTGRESQL_R3_CONTROL),
        ("TEST_ONLY_ROOT_KEK", RecoveryAuthority.EXTERNAL_KEYSTORE),
    ],
)
def test_authority_matrix(field, authority):
    assert RecoveryAuthorityMatrixV1().authority_for(field) == authority


def test_unassigned_authority_rejected():
    with pytest.raises(KeyError):
        RecoveryAuthorityMatrixV1().authority_for("headerSelfAssertedKeyVersion")


def test_snapshot_digest_deterministic_and_excludes_capture_time():
    first = _snapshot()
    second = replace(first, captured_at="2030-01-01T00:00:00Z")
    assert first.snapshot_digest == second.snapshot_digest


def test_snapshot_state_change_changes_digest():
    first = _snapshot()
    second = replace(first, block_number=12)
    assert first.snapshot_digest != second.snapshot_digest
