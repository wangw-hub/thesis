from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import StrEnum
from pathlib import Path
import json


class FormalRunDispositionV1(StrEnum):
    VALID_SUCCESS = "VALID_SUCCESS"
    VALID_EXPECTED_FAIL_CLOSED = "VALID_EXPECTED_FAIL_CLOSED"
    INVALID_INFRASTRUCTURE_FAILURE = "INVALID_INFRASTRUCTURE_FAILURE"
    INVALID_PROTOCOL_VIOLATION = "INVALID_PROTOCOL_VIOLATION"
    INVALID_EVIDENCE_FAILURE = "INVALID_EVIDENCE_FAILURE"
    ABORTED_BY_STOP_RULE = "ABORTED_BY_STOP_RULE"


@dataclass(frozen=True)
class FormalEvidenceClassificationV1:
    formalExperiment: bool
    experimentId: str
    scenarioClass: str
    semanticClass: str

    @classmethod
    def for_config(cls, *, experiment_id: str, scenario_class: str,
                   semantic_class: str) -> "FormalEvidenceClassificationV1":
        if experiment_id not in {"E1", "E2", "E3", "E4", "E5", "WARMUP"}:
            raise ValueError("UNKNOWN_FORMAL_EXPERIMENT")
        return cls(True, experiment_id, scenario_class, semantic_class)

    @classmethod
    def from_dict(cls, value: dict) -> "FormalEvidenceClassificationV1":
        expected = {
            "formalExperiment", "experimentId", "scenarioClass", "semanticClass",
        }
        if type(value) is not dict or set(value) != expected:
            raise ValueError("STRICT_FORMAL_CLASSIFICATION_FIELDS")
        result = cls(**value)
        if type(result.formalExperiment) is not bool or not result.formalExperiment:
            raise ValueError("INVALID_FORMAL_CLASSIFICATION")
        return result

    def to_dict(self) -> dict:
        return asdict(self)

    def labels(self) -> tuple[str, ...]:
        return (
            "FORMAL_EXPERIMENT",
            "R3_FORMAL",
            self.experimentId,
            self.semanticClass,
            self.scenarioClass,
        )

    def validate(self) -> None:
        if self.experimentId in {"E1", "E2", "E3", "E4", "E5"} and not self.scenarioClass:
            raise ValueError("FORMAL_SCENARIO_REQUIRED")


class MaterialReleaseDecisionV2(StrEnum):
    NOT_EVALUATED = "NOT_EVALUATED"
    DENIED = "DENIED"
    ALLOWED = "ALLOWED"
    ALLOWED_AFTER_CURRENT_HEADER_ONLY = "ALLOWED_AFTER_CURRENT_HEADER_ONLY"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class MaterialReleaseEvidenceV2:
    decision: str
    reasonCode: str
    evaluationBlockNumber: int | None
    evaluationBlockHash: str | None
    headerDigest: str | None
    authorizationStateVersion: int | None
    headerVersion: int | None
    evaluated: bool
    sourceComponent: str
    observedAt: str

    def __post_init__(self) -> None:
        decision = MaterialReleaseDecisionV2(self.decision)
        if self.evaluated != (decision is not MaterialReleaseDecisionV2.NOT_EVALUATED):
            raise ValueError("MATERIAL_RELEASE_EVALUATION_FLAG_MISMATCH")
        if decision is MaterialReleaseDecisionV2.DENIED and not self.reasonCode:
            raise ValueError("MATERIAL_RELEASE_DENIAL_REASON_REQUIRED")
        if not self.sourceComponent or not self.observedAt:
            raise ValueError("MATERIAL_RELEASE_PROVENANCE_REQUIRED")

    @classmethod
    def from_dict(cls, value: dict) -> "MaterialReleaseEvidenceV2":
        expected = {
            "decision", "reasonCode", "evaluationBlockNumber", "evaluationBlockHash",
            "headerDigest", "authorizationStateVersion", "headerVersion", "evaluated",
            "sourceComponent", "observedAt",
        }
        if type(value) is not dict or set(value) != expected:
            raise ValueError("STRICT_MATERIAL_RELEASE_EVIDENCE_FIELDS")
        return cls(**value)

    def to_dict(self) -> dict:
        return asdict(self)


def validate_formal_run_evidence(run_root: Path, expected_stage: str) -> tuple[str, ...]:
    """Strict formal run evidence contract (no PILOT labels allowed)."""
    errors: list[str] = []
    required = ("config.json", "run-state.json", "material-release-evidence.json")
    try:
        records = {
            name: json.loads((run_root / name).read_text("utf-8"))
            for name in required
        }
    except (OSError, json.JSONDecodeError) as exc:
        return (f"EVIDENCE_READ:{type(exc).__name__}",)
    classifications: list[FormalEvidenceClassificationV1] = []
    for name in ("config.json", "run-state.json"):
        try:
            classification = FormalEvidenceClassificationV1.from_dict(
                records[name]["evidenceClassification"]
            )
            if tuple(records[name].get("classification", ())) != classification.labels():
                errors.append(f"{name}:CLASSIFICATION_LABEL_MISMATCH")
            if "PILOT_ONLY" in tuple(records[name].get("classification", ())):
                errors.append(f"{name}:PILOT_CLASSIFICATION_PRESENT")
            classifications.append(classification)
        except (KeyError, TypeError, ValueError) as exc:
            errors.append(f"{name}:CLASSIFICATION:{exc}")
    if len(classifications) == 2 and classifications[0] != classifications[1]:
        errors.append("CLASSIFICATION_CONFLICT")
    material_record = records["material-release-evidence.json"]
    try:
        authoritative = MaterialReleaseEvidenceV2.from_dict(material_record["current"])
        history = tuple(
            MaterialReleaseEvidenceV2.from_dict(x) for x in material_record["history"]
        )
        if not history or history[-1] != authoritative:
            errors.append("MATERIAL_RELEASE_HISTORY_TERMINAL_MISMATCH")
        if (
            material_record.get("scenarioProjection") != authoritative.to_dict()
            or material_record.get("finalEnvelopeProjection") != authoritative.to_dict()
        ):
            errors.append("MATERIAL_RELEASE_PROJECTION_CONFLICT")
    except (KeyError, TypeError, ValueError) as exc:
        errors.append(f"MATERIAL_RELEASE:{exc}")
    if expected_stage == "E5":
        try:
            fault = json.loads((run_root / "fault-evidence.json").read_text("utf-8"))
            if fault.get("faultClass", "NONE") != "NONE":
                for field in (
                    "faultId", "faultClass", "scenario", "seed", "expectedOutcome",
                    "actualOutcome", "injectionRequested", "injectionObserved",
                    "observationEvidence", "cleanupRequested", "cleanupCompleted",
                ):
                    if field not in fault or fault[field] in (None, ""):
                        errors.append(f"FAULT_EVIDENCE_MISSING:{field}")
                if fault.get("injectionObserved") is not True:
                    errors.append("FAULT_INDEPENDENT_OBSERVATION_MISSING")
        except (OSError, json.JSONDecodeError, TypeError) as exc:
            errors.append(f"FAULT_EVIDENCE_READ:{type(exc).__name__}")
    return tuple(errors)
