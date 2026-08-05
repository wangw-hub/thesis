import json
from pathlib import Path

from epoch_auth_r3.pilot.phase_contract import contract_for, validate_contract_partition, validate_phase_events


def test_canary_phase_contract_partition_is_total_and_disjoint():
    contract = contract_for("CANARY_INITIAL_END_TO_END")
    validate_contract_partition(contract)
    groups = [set(contract[name]) for name in ("required", "optional", "notApplicable", "forbidden")]
    assert all(not (left & right) for index, left in enumerate(groups) for right in groups[index + 1:])


def test_not_applicable_phase_is_declared_but_not_emitted(tmp_path: Path):
    contract = contract_for("CANARY_INITIAL_END_TO_END")
    required = contract["required"]
    config = {"runId": "r", "attemptId": "a", "configDigest": "c"}
    events = [
        {"runId": "r", "attemptId": "a", "configDigest": "c", "executionHost": "experiment-client",
         "phaseName": name, "phaseSequence": index, "monotonicTimestampNs": index,
         "eventType": event_type, "result": "OK"}
        for index, (name, event_type) in enumerate(
            [(name, kind) for name in required for kind in ("STARTED", "COMPLETED")], 1
        )
    ]
    path = tmp_path / "events.jsonl"
    path.write_text("\n".join(json.dumps(event) for event in events), encoding="utf-8")
    result = validate_phase_events(config, contract, path)
    assert result.valid
    assert result.notApplicableErrors == 0
