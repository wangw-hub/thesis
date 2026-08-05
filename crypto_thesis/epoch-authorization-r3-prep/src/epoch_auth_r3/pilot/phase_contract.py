from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


COMMON_PHASES = frozenset({
    "RUN", "ENVIRONMENT_CHECK", "RESET", "WORKLOAD", "EVIDENCE_SEAL", "RUN_FINISHED",
})
CANARY_PHASES = frozenset({
    "FIXTURE_GENERATION", "BODY_ENCRYPT", "BODY_LOCAL_STORE", "HEADER_BUILD",
    "HEADER_SIGN", "HEADER_LOCAL_STORE", "JOB_CREATE", "CHAIN_TRANSACTION_BROADCAST",
    "CHAIN_WRITE_ADMISSION", "CHAIN_RECEIPT", "COMPOSITE_STATE_READ",
    "DATABASE_FINALIZE", "OBJECT_DIGEST_VERIFY",
    "MATERIAL_RELEASE_RULE_CHECK",
})
SCENARIO_PHASES = {
    "CANARY_INITIAL_END_TO_END": CANARY_PHASES,
    "INITIAL": CANARY_PHASES - {"FIXTURE_GENERATION"},
    "HEADER_ONLY": frozenset({"EVENT_SCAN", "AFFECTED_RESOURCE_RESOLVE", "HEADER_BUILD",
                    "BODY_ENCRYPT", "BODY_LOCAL_STORE", "HEADER_SIGN", "HEADER_LOCAL_STORE",
                    "CHAIN_TRANSACTION_BROADCAST",
                    "JOB_CREATE", "CHAIN_WRITE_ADMISSION", "CHAIN_RECEIPT",
                    "COMPOSITE_STATE_READ", "DATABASE_FINALIZE",
                    "RECIPIENT_INDEX_UPDATE", "MATERIAL_RELEASE_ENABLE"}),
    "BODY_ROTATION": frozenset({"EVENT_SCAN", "AFFECTED_RESOURCE_RESOLVE", "CONTENT_KEY_GENERATE",
                     "BODY_DECRYPT", "BODY_ENCRYPT", "BODY_LOCAL_STORE", "HEADER_BUILD",
                     "HEADER_SIGN", "HEADER_LOCAL_STORE", "CHAIN_TRANSACTION_BROADCAST",
                     "JOB_CREATE", "CHAIN_WRITE_ADMISSION", "CHAIN_RECEIPT",
                     "COMPOSITE_STATE_READ", "DATABASE_FINALIZE",
                     "RECIPIENT_INDEX_UPDATE", "MATERIAL_RELEASE_ENABLE"}),
    "STORAGE": frozenset({"BODY_LOCAL_STORE", "BODY_IPFS_REPLICATE", "IPFS_READBACK_VERIFY"}),
    "FAULT": frozenset({"FAULT_ACTIVATION", "FAULT_OBSERVATION", "RECOVERY_START",
              "RECOVERY_RECONCILIATION", "RECOVERY_COMPLETE"}),
    "IPFS_REPLICATION": frozenset({
        "BODY_LOCAL_STORE", "BODY_IPFS_REPLICATE", "IPFS_READBACK_VERIFY",
        "HEADER_BUILD", "HEADER_SIGN", "HEADER_LOCAL_STORE",
    }),
    "IPFS_RESTORE": frozenset({
        "BODY_LOCAL_STORE", "BODY_IPFS_REPLICATE", "IPFS_READBACK_VERIFY",
        "HEADER_BUILD", "HEADER_SIGN", "HEADER_LOCAL_STORE",
        "RECOVERY_START", "RECOVERY_RECONCILIATION", "RECOVERY_COMPLETE",
        "MATERIAL_RELEASE_RULE_CHECK",
    }),
    "HEADER_UPDATE_PENDING": frozenset({
        "BODY_ENCRYPT", "BODY_LOCAL_STORE", "HEADER_BUILD", "HEADER_SIGN",
        "HEADER_LOCAL_STORE", "JOB_CREATE", "CHAIN_WRITE_ADMISSION",
        "CHAIN_TRANSACTION_BROADCAST", "CHAIN_RECEIPT", "COMPOSITE_STATE_READ",
        "DATABASE_FINALIZE", "MATERIAL_RELEASE_RULE_CHECK",
    }),
    "REVOCATION_AGENT": frozenset({
        "EVENT_SCAN", "AFFECTED_RESOURCE_RESOLVE", "BODY_ENCRYPT", "BODY_LOCAL_STORE",
        "HEADER_BUILD", "HEADER_SIGN",
        "HEADER_LOCAL_STORE", "JOB_CREATE", "CHAIN_WRITE_ADMISSION",
        "CHAIN_TRANSACTION_BROADCAST", "CHAIN_RECEIPT", "COMPOSITE_STATE_READ",
        "DATABASE_FINALIZE", "RECIPIENT_INDEX_UPDATE",
    }),
    "RECOVERY_RECONCILIATION": frozenset({
        "BODY_ENCRYPT", "BODY_LOCAL_STORE", "HEADER_BUILD", "HEADER_SIGN",
        "HEADER_LOCAL_STORE", "JOB_CREATE", "CHAIN_WRITE_ADMISSION",
        "CHAIN_TRANSACTION_BROADCAST", "CHAIN_RECEIPT", "COMPOSITE_STATE_READ",
        "DATABASE_FINALIZE", "RECOVERY_START", "RECOVERY_RECONCILIATION",
        "RECOVERY_COMPLETE", "MATERIAL_RELEASE_RULE_CHECK",
    }),
}
ALL_KNOWN_PHASES = frozenset().union(COMMON_PHASES, *SCENARIO_PHASES.values())


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


def validate_failure_phase_events(contract: dict, path: Path) -> FailurePhaseValidationResult:
    """Validate honest terminal evidence without treating NOT_REACHED as execution."""
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


def _classify(scenario: str, stage: str | None = None) -> str:
    # KUBO_UNAVAILABLE is a storage-replica fault in P9-C but a service fault
    # in the frozen P9-D matrix.  The stage discriminator keeps both contracts
    # explicit without weakening either validator.
    if stage == "P9-D" and scenario in {
        "SCANNER_RESTART", "LEASE_EXPIRED", "POST_CHAIN_DB_FAILURE",
        "COMMIT_UNKNOWN", "POSTGRES_UNAVAILABLE", "BESU_UNAVAILABLE",
        "KUBO_UNAVAILABLE", "RELEASE_WINDOW", "SUPERSEDED_EVENT",
        "INCOMPLETE_INDEX", "ROOT_KEK_UNAVAILABLE", "NO_REPLICA",
    }:
        return "FAULT"
    if scenario in SCENARIO_PHASES:
        return scenario
    if scenario in {"IPFS_REPLICA", "IPFS_RESTORE", "LOCAL_READ", "LOCAL_IPFS",
                    "HEADER_RESTORE", "BODY_RESTORE", "CORRUPT_RESTORE", "KUBO_UNAVAILABLE",
                    "CID_MISMATCH", "BOTH_MISSING"}:
        return "STORAGE"
    if scenario in {"RELEASE_FAIL_CLOSED", "REVOCATION_AGENT", "RECOVERY", "SCANNER_RESTART",
                    "LEASE_EXPIRED", "POST_CHAIN_DB_FAILURE", "COMMIT_UNKNOWN",
                    "POSTGRES_UNAVAILABLE", "BESU_UNAVAILABLE", "RELEASE_WINDOW",
                    "SUPERSEDED_EVENT", "INCOMPLETE_INDEX", "ROOT_KEK_UNAVAILABLE", "NO_REPLICA"}:
        return "FAULT"
    raise ValueError("UNKNOWN_SCENARIO_PHASE_CONTRACT")


def contract_for(scenario: str, stage: str | None = None) -> dict:
    key = _classify(scenario, stage=stage)
    required = COMMON_PHASES | SCENARIO_PHASES[key]
    contract = {
        "schemaVersion": 1,
        "scenarioClass": key,
        "required": sorted(required),
        "optional": [],
        "notApplicable": sorted(ALL_KNOWN_PHASES - required),
        "forbidden": [],
    }
    validate_contract_partition(contract)
    return contract


def validate_contract_partition(contract: dict) -> None:
    expected = {"schemaVersion", "scenarioClass", "required", "optional", "notApplicable", "forbidden"}
    if type(contract) is not dict or set(contract) != expected or contract["schemaVersion"] != 1:
        raise ValueError("INVALID_PHASE_CONTRACT_SHAPE")
    categories = {name: set(contract[name]) for name in ("required", "optional", "notApplicable", "forbidden")}
    if any(len(categories[left] & categories[right]) for left in categories for right in categories if left < right):
        raise ValueError("PHASE_CONTRACT_OVERLAP")
    if set().union(*categories.values()) != set(ALL_KNOWN_PHASES):
        raise ValueError("PHASE_CONTRACT_INCOMPLETE")


def validate_phase_events(config: dict, contract: dict, path: Path) -> PhaseValidationResult:
    validate_contract_partition(contract)
    events = [json.loads(line) for line in path.read_text("utf-8").splitlines() if line.strip()]
    sequence_errors = sum(event.get("phaseSequence") != index for index, event in enumerate(events, 1))
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
    completed = {event["phaseName"] for event in events if event.get("eventType") == "COMPLETED" and event.get("result") == "OK"}
    observed_names = {event.get("phaseName") for event in events}
    missing = tuple(sorted(required - completed))
    forbidden = tuple(sorted(forbidden_set & observed_names))
    # N/A is declared solely by the contract.  It must never be emitted as an executed event.
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
    valid = not (missing or forbidden or sequence_errors or identity_errors or not_applicable_errors or monotonic_errors or start_end_errors)
    return PhaseValidationResult(valid, missing, forbidden, sequence_errors, identity_errors,
                                 not_applicable_errors, monotonic_errors, start_end_errors)
