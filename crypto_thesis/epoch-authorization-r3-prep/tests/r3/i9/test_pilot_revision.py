import json
from dataclasses import replace

import pytest

from epoch_auth_r3.pilot.attempt import R3PilotAttemptIdentityV1
from epoch_auth_r3.pilot.config import (
    attempt_scoped_run_id,
    config_digest,
    validate_remote_authoritative_config,
)
from epoch_auth_r3.pilot.phase_contract import contract_for, validate_phase_events
from epoch_auth_r3.pilot.stage_gate import (
    PilotStageStateV1,
    StageQuality,
    enter_next_stage,
)
from test_pilot_contracts import config


ATTEMPT = "I9_REVISION_1_20260730T120000Z_0123456"


def test_attempt_identity_v1():
    item = R3PilotAttemptIdentityV1(
        1, ATTEMPT, "I9_PIPELINE_REPAIR", "INVALIDATED_I9_ATTEMPT_0",
        "a" * 40, "b" * 64, "2026-07-30T12:00:00Z", "CREATED",
    )
    assert item.attemptId == ATTEMPT


def test_new_attempt_new_run_id_and_same_config_digest():
    cfg = config()
    assert config_digest(cfg) == config_digest(replace(cfg, createdAt="later"))
    assert attempt_scoped_run_id(ATTEMPT, cfg) != attempt_scoped_run_id(
        ATTEMPT.replace("120000", "120001"), cfg
    )


def test_remote_execution_required_and_windows_path_rejected():
    cfg = replace(config(), localObjectStoreRoot=(
        f"/var/lib/epoch-auth-r3/i9-pilot/attempts/{ATTEMPT}/local-store"
    ))
    validate_remote_authoritative_config(cfg, ATTEMPT)
    with pytest.raises(ValueError):
        validate_remote_authoritative_config(
            replace(cfg, localObjectStoreRoot=r"D:\pilot\objects"), ATTEMPT
        )


def test_phase_contract_and_not_applicable(tmp_path):
    contract = contract_for("CANARY_INITIAL_END_TO_END")
    cfg = {"runId": "a" * 64, "attemptId": ATTEMPT, "configDigest": "b" * 64}
    events = []
    sequence = 0
    for phase in contract["required"]:
        for event_type in ("STARTED", "COMPLETED"):
            sequence += 1
            events.append({
                **cfg, "phaseName": phase, "phaseSequence": sequence,
                "eventType": event_type, "executionHost": "experiment-client",
                "monotonicTimestampNs": sequence, "result": "OK",
            })
    path = tmp_path / "events.jsonl"
    path.write_text("\n".join(json.dumps(x) for x in events), encoding="utf-8")
    assert validate_phase_events(cfg, contract, path).valid
    events.append({**cfg, "phaseName": contract["notApplicable"][0],
                   "phaseSequence": sequence + 1, "eventType": "NOT_APPLICABLE",
                   "executionHost": "experiment-client", "monotonicTimestampNs": sequence + 1,
                   "result": "NOT_APPLICABLE"})
    path.write_text("\n".join(json.dumps(x) for x in events), encoding="utf-8")
    assert not validate_phase_events(cfg, contract, path).valid


@pytest.mark.parametrize(
    ("state", "expected"),
    [
        (PilotStageStateV1.P9_A_PASSED, PilotStageStateV1.P9_B_RUNNING),
        (PilotStageStateV1.P9_B_PASSED, PilotStageStateV1.P9_C_RUNNING),
        (PilotStageStateV1.P9_C_PASSED, PilotStageStateV1.P9_D_RUNNING),
    ],
)
def test_stage_gate_allows_only_passed_predecessor(state, expected):
    assert enter_next_stage(state) == expected


@pytest.mark.parametrize(
    "state",
    [
        PilotStageStateV1.P9_A_RUNNING,
        PilotStageStateV1.P9_A_FAILED,
        PilotStageStateV1.P9_B_FAILED,
        PilotStageStateV1.P9_C_FAILED,
    ],
)
def test_stage_gate_blocks_downstream(state):
    with pytest.raises(ValueError, match="PILOT_STAGE_GATE_BLOCKED"):
        enter_next_stage(state)


def test_stage_gate_requires_all_valid():
    assert StageQuality(8, 8, 8).passed()
    assert not StageQuality(8, 8, 7).passed()
    assert not StageQuality(8, 8, 8, rawShaErrors=1).passed()


def test_expected_fail_closed_can_be_valid():
    state = {
        "valid": True,
        "outcomeClass": "FAIL_CLOSED_EXPECTED",
        "invariantViolations": 0,
    }
    assert state["valid"] and state["outcomeClass"].endswith("_EXPECTED")
