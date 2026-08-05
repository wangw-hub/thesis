from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import StrEnum
from typing import Callable, Iterable

from epoch_auth_r3.pilot.attempt import PilotAttemptIdV1
from epoch_auth_r3.pilot.p9a_evidence_contract import (
    P9AAcceptanceDecisionV1, PilotEvidenceClassificationV1,
)


P9A_RUN_DOMAIN = b"EPOCH_AUTH_R3_I9_PILOT_RUN_ATTEMPT_V1"
P9A_LABELS = PilotEvidenceClassificationV1.for_stage(
    "P9-A", "UNBOUND_SCENARIO"
).labels()


class P9AState(StrEnum):
    READY = "P9_A_READY"
    RUNNING = "P9_A_RUNNING"
    PASSED = "P9_A_PASSED"
    FAILED = "P9_A_FAILED"


@dataclass(frozen=True)
class P9AScenarioV1:
    scenario_id: str
    scenario_class: str
    seed: int
    expected_outcome_class: str
    expected_transaction_count: int

    def canonical_dict(self) -> dict:
        return {
            "expectedOutcomeClass": self.expected_outcome_class,
            "expectedTransactionCount": self.expected_transaction_count,
            "scenarioClass": self.scenario_class,
            "scenarioId": self.scenario_id,
            "seed": self.seed,
        }

    @property
    def config_digest(self) -> str:
        raw = json.dumps(
            self.canonical_dict(), sort_keys=True, separators=(",", ":")
        ).encode()
        return hashlib.sha256(raw).hexdigest()

    def run_id(self, attempt_id: str) -> str:
        attempt_id = PilotAttemptIdV1.validate(attempt_id).serialize()
        return hashlib.sha256(
            P9A_RUN_DOMAIN + attempt_id.encode() + self.config_digest.encode()
        ).hexdigest()


P9A_SCENARIOS = (
    P9AScenarioV1("P9_A_A1_INITIAL", "INITIAL", 91001, "SUCCESS_EXPECTED", 2),
    P9AScenarioV1("P9_A_A2_HEADER_ONLY", "HEADER_ONLY", 91002, "SUCCESS_EXPECTED", 3),
    P9AScenarioV1("P9_A_A3_BODY_ROTATION", "BODY_ROTATION", 91003, "SUCCESS_EXPECTED", 3),
    P9AScenarioV1("P9_A_A4_IPFS_REPLICATION", "IPFS_REPLICATION", 91004, "SUCCESS_EXPECTED", 0),
    P9AScenarioV1("P9_A_A5_IPFS_RESTORE", "IPFS_RESTORE", 91005, "RECOVERY_EXPECTED", 0),
    P9AScenarioV1(
        "P9_A_A6_HEADER_UPDATE_PENDING",
        "HEADER_UPDATE_PENDING",
        91006,
        "FAIL_CLOSED_EXPECTED",
        3,
    ),
    P9AScenarioV1(
        "P9_A_A7_REVOCATION_AGENT", "REVOCATION_AGENT", 91007, "SUCCESS_EXPECTED", 4
    ),
    P9AScenarioV1(
        "P9_A_A8_RECOVERY_RECONCILIATION",
        "RECOVERY_RECONCILIATION",
        91008,
        "RECOVERY_EXPECTED",
        2,
    ),
)


def validate_p9a_matrix(
    scenarios: Iterable[P9AScenarioV1], *, attempt_id: str
) -> tuple[P9AScenarioV1, ...]:
    rows = tuple(scenarios)
    if len(rows) != 8:
        raise ValueError("P9A_REQUIRES_EXACTLY_EIGHT_CONFIGS")
    for attribute, error in (
        ("scenario_id", "P9A_SCENARIO_ID_DUPLICATE"),
        ("seed", "P9A_SEED_DUPLICATE"),
        ("config_digest", "P9A_CONFIG_DIGEST_DUPLICATE"),
    ):
        values = [getattr(row, attribute) for row in rows]
        if len(values) != len(set(values)):
            raise ValueError(error)
    run_ids = [row.run_id(attempt_id) for row in rows]
    if len(run_ids) != len(set(run_ids)):
        raise ValueError("P9A_RUN_ID_DUPLICATE")
    return rows


def run_p9a_serially(
    scenarios: Iterable[P9AScenarioV1],
    execute: Callable[[P9AScenarioV1], dict],
) -> tuple[dict, ...]:
    results = []
    for scenario in scenarios:
        result = execute(scenario)
        results.append(result)
        if not result.get("valid", False):
            break
    return tuple(results)


def final_p9a_state(results: Iterable[dict]) -> P9AState:
    rows = tuple(results)
    decision = P9AAcceptanceDecisionV1.evaluate(
        planned=8, actual=len(rows),
        valid=sum(bool(row.get("valid", False)) for row in rows),
        classification_errors=sum(int(row.get("classificationErrors", 0)) for row in rows),
        phase_errors=sum(int(row.get("missingPhases", 0)) for row in rows),
        raw_sha_errors=sum(int(row.get("rawShaErrors", 0)) for row in rows),
        material_release_errors=sum(int(row.get("materialReleaseErrors", 0)) for row in rows),
        major=sum(int(row.get("major", 0)) for row in rows),
    )
    return P9AState.PASSED if decision.accepted else P9AState.FAILED
