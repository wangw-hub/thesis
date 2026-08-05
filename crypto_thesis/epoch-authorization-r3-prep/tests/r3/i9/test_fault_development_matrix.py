from pathlib import Path

from scripts.r3_i9 import run_fault_development_matrix as matrix


def test_fault_matrix_has_exact_f1_f8():
    source = Path(matrix.__file__).read_text("utf-8")
    assert [f'"F{i}"' in source for i in range(1, 9)] == [True] * 8


def test_fault_evidence_is_never_pilot_or_formal():
    assert "DEVELOPMENT_ONLY" in matrix.LABELS
    assert "NOT_PILOT_EVIDENCE" in matrix.LABELS
    assert "NOT_FOR_THESIS_RESULTS" in matrix.LABELS
    assert "DO_NOT_REUSE_FOR_PILOT" in matrix.LABELS


def test_commit_unknown_requires_real_broadcast_identity():
    source = Path(matrix.__file__).read_text("utf-8")
    for field in ("transactionHash", "sender", "nonce", "method"):
        assert field in source


def test_f1_never_calls_chain_client():
    source = matrix.f1_uncommitted_job.__code__.co_names
    assert not {"w3", "web3", "_signed_tx"}.intersection(source)


def test_fault_database_role_is_a_frozen_role():
    source = Path(matrix.__file__).read_text("utf-8")
    assert "PilotDatabaseConnectionRoleV1.JOB" in source
    assert "PilotDatabaseConnectionRoleV1.JOB_CREATE" not in source


def test_f5_uses_controlled_recovery_delete():
    assert "controlled_delete_for_recovery_test" in matrix.f5_restore.__code__.co_names
