from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


COMMON_PHASES = frozenset({
    "RUN", "ENVIRONMENT_CHECK", "RESET", "WORKLOAD", "EVIDENCE_SEAL", "RUN_FINISHED",
})
CORE_PHASES = frozenset({
    "CONTENT_KEY_GENERATE", "BODY_DECRYPT", "BODY_ENCRYPT", "BODY_LOCAL_STORE",
    "RECIPIENT_ENVELOPE", "HEADER_BUILD", "HEADER_SIGN", "HEADER_LOCAL_STORE",
    "JOB_CREATE", "CHAIN_WRITE_ADMISSION", "CHAIN_TRANSACTION_BROADCAST",
    "CHAIN_RECEIPT", "COMPOSITE_STATE_READ", "DATABASE_FINALIZE",
    "OBJECT_DIGEST_VERIFY", "MATERIAL_RELEASE_RULE_CHECK",
})
EVENT_PHASES = frozenset({"EVENT_SCAN", "AFFECTED_RESOURCE_RESOLVE"})
REPLICA_PHASES = frozenset({
    "BODY_IPFS_REPLICATE", "IPFS_READBACK_VERIFY",
})
RECOVERY_PHASES = frozenset({
    "RECOVERY_START", "RECOVERY_RECONCILIATION", "RECOVERY_COMPLETE",
})
FAULT_PHASES = frozenset({"FAULT_ACTIVATION", "FAULT_OBSERVATION"})
UPDATE_CLOSE_PHASES = frozenset({"RECIPIENT_INDEX_UPDATE", "MATERIAL_RELEASE_ENABLE"})

SCENARIO_PHASES = {
    "INITIAL": CORE_PHASES - {"RECIPIENT_ENVELOPE"},
    "HEADER_ONLY": EVENT_PHASES | CORE_PHASES | UPDATE_CLOSE_PHASES,
    "BODY_ROTATION": EVENT_PHASES | CORE_PHASES | UPDATE_CLOSE_PHASES,
    "REVOCATION": EVENT_PHASES | CORE_PHASES | {"MATERIAL_RELEASE_ENABLE"},
    "HEADER_UPDATE_PENDING": CORE_PHASES | {"MATERIAL_RELEASE_RULE_CHECK"},
    "RESTORE_LOCAL": CORE_PHASES - {"RECIPIENT_ENVELOPE"} | RECOVERY_PHASES,
    "RESTORE_REPLICA": CORE_PHASES | REPLICA_PHASES | RECOVERY_PHASES,
    "FAULT": FAULT_PHASES | RECOVERY_PHASES | CORE_PHASES,
}
ALL_KNOWN_PHASES = frozenset().union(
    COMMON_PHASES, *SCENARIO_PHASES.values()
)


@dataclass(frozen=True)
class PhaseValidationResult:
    valid: bool
    missing: tuple[str, ...]
    forbidden: tuple[str, ...]
    sequenceErrors: int
    identityErrors: int
    notApplicableErrors: int
    monotonicErrors: int = 0
    startEndErrors: int = 0


@dataclass(frozen=True)
class FailurePhaseValidationResult:
    valid: bool
    missingTerminalEvents: tuple[str, ...]
    unclassifiedRequiredPhases: tuple[str, ...]
    notReachedErrors: int


def validate_contract_partition(contract: dict) -> None:
    expected = {"schemaVersion", "scenarioClass", "required", "optional", "notApplicable", "forbidden"}
    if type(contract) is not dict or set(contract) != expected or contract["schemaVersion"] != 1:
        raise ValueError("INVALID_PHASE_CONTRACT_SHAPE")
    categories = {
        name: set(contract[name]) for name in ("required", "optional", "notApplicable", "forbidden")
    }
    if any(
        len(categories[left] & categories[right])
        for left in categories for right in categories if left < right
    ):
        raise ValueError("PHASE_CONTRACT_OVERLAP")
    if set().union(*categories.values()) != set(ALL_KNOWN_PHASES):
        raise ValueError("PHASE_CONTRACT_INCOMPLETE")


def contract_for(scenario: str, *, replica_state: str | None = None,
                 fault: str | None = None, restore_path: bool = False) -> dict:
    required = COMMON_PHASES | CORE_PHASES
    if scenario == "INITIAL":
        required = required - {"RECIPIENT_ENVELOPE"}
    elif scenario in {"HEADER_ONLY", "BODY_ROTATION"}:
        required = required | EVENT_PHASES | UPDATE_CLOSE_PHASES
    elif scenario == "REVOCATION":
        required = required | EVENT_PHASES | {"MATERIAL_RELEASE_ENABLE"}
    elif scenario == "HEADER_UPDATE_PENDING":
        required = required | {"MATERIAL_RELEASE_RULE_CHECK"}
    elif scenario in {"RESTORE_LOCAL", "RESTORE_REPLICA"}:
        if scenario == "RESTORE_LOCAL":
            required = required - {"RECIPIENT_ENVELOPE"}
        if replica_state == "KUBO_REPLICA" and fault != "BOTH_MISSING":
            required = required | REPLICA_PHASES
        if restore_path and fault == "NONE":
            required = required | RECOVERY_PHASES
    else:
        raise ValueError("UNKNOWN_SCENARIO_PHASE_CONTRACT")
    if fault in {"CORRUPT_RESTORE", "CID_MISMATCH", "BOTH_MISSING"}:
        required = required | FAULT_PHASES
    contract = {
        "schemaVersion": 1,
        "scenarioClass": scenario,
        "required": sorted(required),
        "optional": [],
        "notApplicable": sorted(ALL_KNOWN_PHASES - required),
        "forbidden": [],
    }
    validate_contract_partition(contract)
    return contract


def validate_failure_phase_events(contract: dict, path: Path) -> FailurePhaseValidationResult:
    validate_contract_partition(contract)
    events = [json.loads(line) for line in path.read_text("utf-8").splitlines() if line.strip()]
    completed = {
        event["phaseName"] for event in events
        if event.get("eventType") == "COMPLETED"
    }
    not_reached = {
        event["phaseName"] for event in events
        if event.get("eventType") == "NOT_REACHED"
    }
    required = set(contract["required"])
    classified = completed | not_reached
    terminals = {"RUN_FAILURE_OBSERVED", "EVIDENCE_SEAL", "RUN_FINISHED"}
    missing_terminal = tuple(sorted(terminals - completed))
    unclassified = tuple(sorted(required - classified))
    not_reached_errors = sum(
        event.get("eventType") == "NOT_REACHED"
        and event.get("phaseName") not in required
        for event in events
    )
    valid = not (missing_terminal or unclassified or not_reached_errors)
    return FailurePhaseValidationResult(
        valid, missing_terminal, unclassified, not_reached_errors,
    )


def validate_phase_events(config: dict, contract: dict, path: Path) -> PhaseValidationResult:
    validate_contract_partition(contract)
    events = [json.loads(line) for line in path.read_text("utf-8").splitlines() if line.strip()]
    sequence_errors = sum(
        event.get("phaseSequence") != index for index, event in enumerate(events, 1)
    )
    identity_errors = sum(
        event.get("runId") != config["runId"]
        or event.get("attemptId") != config["attemptId"]
        or event.get("configDigest") != config["configDigest"]
        or event.get("executionHost") != "experiment-client"
        for event in events
    )
    required = set(contract["required"])
    not_applicable = set(contract["notApplicable"])
    forbidden_set = set(contract["forbidden"])
    completed = {
        event["phaseName"] for event in events
        if event.get("eventType") == "COMPLETED" and event.get("result") == "OK"
    }
    observed_names = {event.get("phaseName") for event in events}
    missing = tuple(sorted(required - completed))
    forbidden = tuple(sorted(forbidden_set & observed_names))
    not_applicable_errors = len(not_applicable & observed_names) + sum(
        event.get("eventType") == "NOT_APPLICABLE" for event in events
    )
    monotonic_errors = sum(
        events[index]["monotonicTimestampNs"] < events[index - 1]["monotonicTimestampNs"]
        for index in range(1, len(events))
    )
    starts: dict[str, int] = {}
    start_end_errors = 0
    for event in events:
        name = event.get("phaseName")
        if event.get("eventType") == "STARTED":
            starts[name] = starts.get(name, 0) + 1
        elif event.get("eventType") == "COMPLETED":
            starts[name] = starts.get(name, 0) - 1
            if starts[name] < 0:
                start_end_errors += 1
    start_end_errors += sum(abs(value) for value in starts.values())
    valid = not (
        missing or forbidden or sequence_errors or identity_errors
        or not_applicable_errors or monotonic_errors or start_end_errors
    )
    return PhaseValidationResult(
        valid, missing, forbidden, sequence_errors, identity_errors,
        not_applicable_errors, monotonic_errors, start_end_errors,
    )
