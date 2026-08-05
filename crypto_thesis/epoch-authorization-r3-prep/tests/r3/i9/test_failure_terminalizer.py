import json
import socket
from dataclasses import dataclass

import pytest

from epoch_auth_r3.pilot.events import PhaseEventJournal
from epoch_auth_r3.pilot.phase_contract import (
    contract_for, validate_failure_phase_events,
)
from epoch_auth_r3.pilot.terminalizer import PilotRunTerminalizerV1


@dataclass
class Config:
    value: str = "test"


def test_failure_terminalizer(monkeypatch, tmp_path):
    monkeypatch.setattr(socket, "gethostname", lambda: "experiment-client")
    attempt = "revision-7-test"
    run_id = "a" * 64
    journal = PhaseEventJournal(
        tmp_path / "events.jsonl", run_id=run_id,
        attempt_id=attempt, config_digest="b" * 64,
    )
    journal.emit("RUN", "STARTED")
    journal.emit("RUN", "COMPLETED", "FAIL_CLOSED", "SyntheticFailure")
    raw = tmp_path / "raw"
    raw.mkdir()
    result = PilotRunTerminalizerV1(
        journal=journal, contract=contract_for("CANARY_INITIAL_END_TO_END"),
        raw_root=raw, config=Config(),
        common={"attemptId": attempt, "runId": run_id, "configDigest": "b" * 64},
        failure_point="JOB_CREATE",
    ).terminalize(RuntimeError("SYNTHETIC_FAIL_CLOSED"))
    assert result["terminalEvidence"]
    assert result["rawShaErrors"] == 0
    events = (tmp_path / "events.jsonl").read_text()
    assert '"phaseName":"EVIDENCE_SEAL"' in events
    assert '"phaseName":"RUN_FINISHED"' in events
    assert '"eventType":"NOT_REACHED"' in events
    assert validate_failure_phase_events(
        contract_for("CANARY_INITIAL_END_TO_END"), tmp_path / "events.jsonl"
    ).valid
    state = json.loads((raw / run_id / "run-state.json").read_text())
    assert state["status"] == "FAILED_EVIDENCE_SEALED"
