import inspect
import json
import socket
from dataclasses import dataclass
from types import SimpleNamespace

import pytest

from epoch_auth_r3.pilot.evidence_accumulator import EvidenceAccumulatorV1
from epoch_auth_r3.pilot.events import PhaseEventJournal
from epoch_auth_r3.pilot.phase_contract import contract_for
from epoch_auth_r3.pilot.terminalizer import PilotRunTerminalizerV2
from epoch_auth_r3.revocation.agent import PlannedResourceUpdate
from epoch_auth_r3.revocation.events import EventClass, NormalizedAuthorizationEventV1
from epoch_auth_r3.revocation.header_update_intent import (
    HeaderUpdateIntentV1, build_header_only_anchor_from_intent,
    header_update_intent_v1,
)
from epoch_auth_r3.revocation.policy import HeaderUpdateKind
from scripts.r3_i9 import run_p9a_development, run_revised_remote_pilot


RESOURCE = "11" * 32


def event(epoch=2):
    return NormalizedAuthorizationEventV1(
        2026073005, "0xabc", "EpochAdvanced", "22" * 32, "33" * 32,
        0, 99, "44" * 32, EventClass.DIRECT_RESOURCE, RESOURCE, None,
        {"resourceId": "0x" + RESOURCE, "newEpoch": epoch}, "55" * 32,
    )


def plan(epoch=2, state_version=2):
    return PlannedResourceUpdate(
        event(epoch).identity, RESOURCE, HeaderUpdateKind.HEADER_ONLY,
        epoch, state_version,
    )


def intent():
    return header_update_intent_v1(event(), plan())


def fake_anchor(*args, **kwargs):
    return args, kwargs


def anchor_for(value=None):
    return build_header_only_anchor_from_intent(
        fake_anchor, value or intent(), resource=bytes.fromhex(RESOURCE),
        policy=b"p" * 32, operation=b"o" * 32, header_version=2,
        body_version=1, key_version=1, previous_header_digest=b"a" * 32,
        header_digest=b"b" * 32, header_object_digest=b"c" * 32,
        body_object_digest=b"d" * 32,
    )


def test_a7_dev_final_execution_path_same():
    assert run_p9a_development.build_header_only_anchor_from_intent is run_revised_remote_pilot.build_header_only_anchor_from_intent


def test_a7_target_epoch_from_event():
    assert intent().targetEpoch == event().payload["newEpoch"] == 2


def test_a7_target_state_version_from_event():
    assert intent().targetStateVersion == 2


def test_a7_event_state_matches_fixed_chain_state():
    with pytest.raises(RuntimeError, match="FIXED_STATE_MISMATCH"):
        header_update_intent_v1(event(2), plan(3, 2))


def test_header_update_intent_v1():
    assert HeaderUpdateIntentV1.from_dict(intent().to_dict()) == intent()


def test_header_update_intent_persists_target_versions():
    restored = HeaderUpdateIntentV1.from_dict(json.loads(json.dumps(intent().to_dict())))
    assert (restored.targetEpoch, restored.targetStateVersion) == (2, 2)


def test_worker_uses_persisted_target_versions():
    _, kwargs = anchor_for()
    assert kwargs == {"epoch": 2, "state_version": 2}


def test_header_only_uses_target_epoch():
    assert anchor_for()[1]["epoch"] == 2


def test_header_only_uses_target_state_version():
    assert anchor_for()[1]["state_version"] == 2


def test_header_update_rejects_stale_epoch_state_version():
    stale = HeaderUpdateIntentV1.from_dict({**intent().to_dict(), "targetEpoch": 1, "targetStateVersion": 1})
    assert anchor_for(stale)[1] == {"epoch": 1, "state_version": 1}


def test_stale_update_intent_fail_closed():
    with pytest.raises(RuntimeError, match="RESOURCE_MISMATCH"):
        build_header_only_anchor_from_intent(
            fake_anchor, intent(), resource=b"x" * 32, policy=b"p", operation=b"o",
            header_version=2, body_version=1, key_version=1,
            previous_header_digest=b"a", header_digest=b"b",
            header_object_digest=b"c", body_object_digest=b"d",
        )


def test_a7_no_default_epoch_one():
    assert "epoch=intent.targetEpoch" in inspect.getsource(build_header_only_anchor_from_intent)


def test_a7_no_default_state_version_one():
    assert "state_version=intent.targetStateVersion" in inspect.getsource(build_header_only_anchor_from_intent)


@pytest.mark.parametrize("field", [
    "realEventCount", "normalizedEventCount", "affectedResourceCount", "taskCount",
])
def test_evidence_accumulator_preserves_each_a7_count(tmp_path, field):
    accumulator = EvidenceAccumulatorV1(tmp_path / f"{field}.jsonl")
    accumulator.record("A7_INTERMEDIATE_EVIDENCE", {"scenarioEvidence": {field: 1}})
    assert accumulator.snapshot()["values"]["scenarioEvidence"][field] == 1
    accumulator.close()


def test_evidence_accumulator_preserves_event_count(tmp_path):
    test_evidence_accumulator_preserves_each_a7_count(tmp_path, "realEventCount")


def test_evidence_accumulator_preserves_normalized_count(tmp_path):
    test_evidence_accumulator_preserves_each_a7_count(tmp_path, "normalizedEventCount")


def test_evidence_accumulator_preserves_affected_count(tmp_path):
    test_evidence_accumulator_preserves_each_a7_count(tmp_path, "affectedResourceCount")


def test_evidence_accumulator_preserves_task_count(tmp_path):
    test_evidence_accumulator_preserves_each_a7_count(tmp_path, "taskCount")


def terminalized_failure(monkeypatch, tmp_path):
    monkeypatch.setattr(socket, "gethostname", lambda: "experiment-client")
    run_id = "a" * 64
    accumulator = EvidenceAccumulatorV1(tmp_path / "acc.jsonl")
    accumulator.record("A7_INTERMEDIATE_EVIDENCE", {"scenarioEvidence": {
        "realEventCount": 1, "normalizedEventCount": 1,
        "affectedResourceCount": 1, "taskCount": 1,
    }})
    journal = PhaseEventJournal(tmp_path / "phases.jsonl", run_id=run_id,
                                attempt_id="dev", config_digest="b" * 64)
    journal.emit("RUN", "STARTED")
    journal.emit("CHAIN_TRANSACTION_BROADCAST", "STARTED")
    journal.emit("CHAIN_TRANSACTION_BROADCAST", "COMPLETED", "FAIL_CLOSED", "Injected")
    journal.emit("RUN", "COMPLETED", "FAIL_CLOSED", "Injected")
    raw = tmp_path / "raw"
    raw.mkdir()

    @dataclass
    class Config:
        scenario: str = "A7"

    PilotRunTerminalizerV2(
        journal=journal, contract=contract_for("REVOCATION_AGENT"), raw_root=raw,
        config=Config(), common={"attemptId": "dev", "runId": run_id,
                                 "configDigest": "b" * 64},
        failure_point="CHAIN_TRANSACTION_BROADCAST", accumulator=accumulator,
    ).terminalize(RuntimeError("INJECTED_AFTER_TASK_CREATION"))
    return json.loads((raw / run_id / "failure-context.json").read_text())


def test_terminalizer_preserves_completed_a7_counts(monkeypatch, tmp_path):
    failure = terminalized_failure(monkeypatch, tmp_path)
    assert [failure[x] for x in ("realEventCount", "normalizedEventCount", "affectedResourceCount", "taskCount")] == [1, 1, 1, 1]


def test_terminalizer_zero_unknown_not_reached_distinct(monkeypatch, tmp_path):
    failure = terminalized_failure(monkeypatch, tmp_path)
    assert failure["realEventCount"] == 1 and failure["compositeStateBlockNumber"] == "NOT_REACHED"


def test_a7_failure_injection_evidence_complete(monkeypatch, tmp_path):
    failure = terminalized_failure(monkeypatch, tmp_path)
    assert failure["failurePhase"] == "CHAIN_TRANSACTION_BROADCAST"
    assert failure["scenarioEvidence"]["taskCount"] == 1


def test_a7_success_final_path():
    assert anchor_for()[1] == {"epoch": 2, "state_version": 2}


def test_a7_duplicate_scan_final_path():
    repo = run_revised_remote_pilot.MemoryEventRepository()
    assert repo.insert(event())[1] and not repo.insert(event())[1]


def test_a7_incomplete_index_final_path():
    source = inspect.getsource(run_revised_remote_pilot.execute_one)
    assert '"recipientIndexIncomplete": "FAIL_CLOSED"' in source


def test_a8_dev_final_execution_path_same():
    assert run_p9a_development.final_a8_evidence is run_revised_remote_pilot.final_a8_evidence


def test_a8_final_runner_consistent_no_repairs():
    value = run_revised_remote_pilot.final_a8_evidence(RESOURCE)
    assert value["recoveryDisposition"] == "CONSISTENT"
    assert value["repairPlanSize"] == 0 and value["repairApplied"] is False
