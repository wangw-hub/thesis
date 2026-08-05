import json
import socket
from dataclasses import dataclass

import pytest

from epoch_auth_r3.pilot.chain_write import (
    PilotChainWriteAdmissionGuardV1, PilotChainWritePlanV1,
    PilotChainWriteStepV1,
)
from epoch_auth_r3.pilot.evidence_accumulator import EvidenceAccumulatorV1
from epoch_auth_r3.pilot.events import PhaseEventJournal
from epoch_auth_r3.pilot.phase_contract import contract_for
from epoch_auth_r3.pilot.terminalizer import PilotRunTerminalizerV2


def plan():
    return PilotChainWritePlanV1(
        "attempt", "a" * 64, "b" * 64, "c" * 64, "d" * 64, 2,
        (
            PilotChainWriteStepV1(1, "auth", "registerResource", "owner", "pending"),
            PilotChainWriteStepV1(2, "registry", "commitHeaderV1", "committer", "pending"),
        ),
    )


def test_chain_write_plan_v1_and_unexpected_count_rejected():
    assert plan().expectedTransactionCount == 2
    with pytest.raises(ValueError, match="COUNT"):
        PilotChainWritePlanV1(
            "a", "b", "c", "d", "e", 1, plan().transactionSequence
        )


def test_chain_write_requires_committed_visible_job_and_verified_objects():
    admitted = PilotChainWriteAdmissionGuardV1.admit(
        plan=plan(),
        visibility={
            "status": "READY_FOR_CHAIN_SUBMISSION",
            "visibleFromIndependentConnection": True,
        },
        object_verification={"headerVerified": True, "bodyVerified": True},
        chain_writes_before_admission=0,
    )
    assert admitted["decision"] == "ADMITTED"
    with pytest.raises(RuntimeError, match="JOB_CREATE"):
        PilotChainWriteAdmissionGuardV1.admit(
            plan=plan(), visibility={"status": "CREATED"},
            object_verification={"headerVerified": True, "bodyVerified": True},
            chain_writes_before_admission=0,
        )
    with pytest.raises(RuntimeError, match="CHAIN_WRITE_BEFORE"):
        PilotChainWriteAdmissionGuardV1.admit(
            plan=plan(),
            visibility={
                "status": "READY_FOR_CHAIN_SUBMISSION",
                "visibleFromIndependentConnection": True,
            },
            object_verification={"headerVerified": True, "bodyVerified": True},
            chain_writes_before_admission=1,
        )


def test_evidence_accumulator_append_only_and_terminalizer_preserves_context(
    monkeypatch, tmp_path,
):
    monkeypatch.setattr(socket, "gethostname", lambda: "experiment-client")
    run_id = "a" * 64
    attempt = "attempt"
    accumulator = EvidenceAccumulatorV1(tmp_path / "accumulator.jsonl")
    accumulator.record("OBJECTS", {
        "headerDigest": "1" * 64,
        "headerObjectDigest": "2" * 64,
        "bodyObjectDigest": "3" * 64,
    })
    receipt = {
        "transactionHash": "4" * 64, "nonce": 7, "blockNumber": 8,
        "blockHash": "5" * 64, "receiptStatus": 1,
    }
    accumulator.append_transaction("broadcastTransactions", receipt)
    accumulator.append_transaction("receipts", receipt)
    journal = PhaseEventJournal(
        tmp_path / "phase.jsonl", run_id=run_id, attempt_id=attempt,
        config_digest="6" * 64,
    )
    journal.emit("RUN", "STARTED")
    journal.emit("DATABASE_FINALIZE", "STARTED")
    journal.emit("DATABASE_FINALIZE", "COMPLETED", "FAIL_CLOSED", "Synthetic")
    journal.emit("RUN", "COMPLETED", "FAIL_CLOSED", "Synthetic")
    raw = tmp_path / "raw"
    raw.mkdir()

    @dataclass
    class Config:
        value: str = "test"

    result = PilotRunTerminalizerV2(
        journal=journal, contract=contract_for("CANARY_INITIAL_END_TO_END"),
        raw_root=raw, config=Config(),
        common={"attemptId": attempt, "runId": run_id, "configDigest": "6" * 64},
        failure_point="RUN", accumulator=accumulator,
    ).terminalize(RuntimeError("DATABASE_TRANSACTION_ABORTED"))
    failure = json.loads((raw / run_id / "failure-context.json").read_text())
    assert result["failurePoint"] == "DATABASE_FINALIZE"
    assert failure["headerDigest"] == "1" * 64
    assert failure["bodyObjectDigest"] == "3" * 64
    assert failure["transactionHashes"] == ["4" * 64]
    assert failure["receipts"][0]["blockNumber"] == 8
    assert (raw / run_id / "payload-artifact-sha256.json").exists()
    assert (raw / run_id / "final-run-envelope-sha256.json").exists()


def test_non_pilot_database_error_taxonomy():
    source = __import__(
        "inspect"
    ).getsource(__import__(
        "epoch_auth_r3.pilot.database", fromlist=["PilotDatabaseConnectionFactoryV1"]
    ).PilotDatabaseConnectionFactoryV1)
    assert "PILOT_DATABASE_IDENTITY_MISMATCH" in source
    assert "NON_PILOT_DATABASE" not in source
