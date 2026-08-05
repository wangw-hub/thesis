import json

import pytest

from epoch_auth_r3.pilot.p9a_stage_terminalizer import P9AStageTerminalizerV1
from epoch_auth_r3.pilot.p9a_evidence_contract import P9AAcceptanceDecisionV1


ATTEMPT = "I9_P9A_20260801T080000Z_793adab"


def gate():
    return {
        "schemaVersion": 1,
        "revision": 0,
        "attemptId": ATTEMPT,
        "canary": "CANARY_PASSED",
        "state": "P9_A_READY",
        "history": [],
        "p9BTasksCreated": False,
    }


def test_p9a_stage_terminalizer_atomic_update_and_readback(tmp_path):
    path = tmp_path / "stage-gate-state.json"
    path.write_text(json.dumps(gate()), encoding="utf-8")
    terminalizer = P9AStageTerminalizerV1(path, ATTEMPT)
    terminalizer.start()
    evidence = terminalizer.finish(
        decision=P9AAcceptanceDecisionV1.evaluate(planned=8, actual=8, valid=8),
        planned=8, actual=8, valid=8,
    )
    final = json.loads(path.read_text("utf-8"))
    assert final["state"] == "P9_A_PASSED"
    assert final["revision"] == 2
    assert evidence["readbackVerified"] is True
    assert evidence["gateSha256"]


def test_p9a_gate_rejects_acceptance_count_mismatch(tmp_path):
    path = tmp_path / "stage-gate-state.json"
    path.write_text(json.dumps(gate()), encoding="utf-8")
    terminalizer = P9AStageTerminalizerV1(path, ATTEMPT)
    terminalizer.start()
    decision = P9AAcceptanceDecisionV1.evaluate(planned=8, actual=8, valid=8)
    with pytest.raises(ValueError, match="P9A_ACCEPTANCE_DECISION_COUNT_MISMATCH"):
        terminalizer.finish(
            decision=decision, planned=8, actual=8, valid=0,
        )


@pytest.mark.parametrize("failure_point", ["BOOTSTRAP", "RUN_ID", "A1"])
def test_p9a_exception_sets_failed_and_never_remains_running(tmp_path, failure_point):
    path = tmp_path / "stage-gate-state.json"
    path.write_text(json.dumps(gate()), encoding="utf-8")
    terminalizer = P9AStageTerminalizerV1(path, ATTEMPT)
    with pytest.raises(RuntimeError, match="synthetic"):
        with terminalizer.guard(failed_scenario="A1"):
            raise RuntimeError(f"synthetic-{failure_point}")
    final = json.loads(path.read_text("utf-8"))
    assert final["state"] == "P9_A_FAILED"
    assert final["failureScope"] == "ATTEMPT_ORCHESTRATION"
    assert final["failedScenario"] == "A1"
    assert final["runCreated"] is False
    assert final["businessSideEffects"] is False


def test_p9a_failure_stops_next_scenario_without_fake_run(tmp_path):
    path = tmp_path / "stage-gate-state.json"
    path.write_text(json.dumps(gate()), encoding="utf-8")
    called = []
    terminalizer = P9AStageTerminalizerV1(path, ATTEMPT)
    with pytest.raises(ValueError):
        with terminalizer.guard(failed_scenario="A1"):
            called.append("A1")
            raise ValueError("boom")
    assert called == ["A1"]
    assert not list(tmp_path.glob("**/run-state.json"))
