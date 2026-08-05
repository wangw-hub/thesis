from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import StrEnum
from pathlib import Path
import json


class PilotPhaseV1(StrEnum):
    P9_A_SMOKE_ONLY = "P9_A_SMOKE_ONLY"
    P9_B = "P9_B"
    P9_C = "P9_C"
    P9_D = "P9_D"
    DEVELOPMENT_ONLY = "DEVELOPMENT_ONLY"


@dataclass(frozen=True)
class PilotEvidenceClassificationV1:
    pilotOnly: bool
    pilotPhase: str
    scenarioClass: str
    formalResultEligible: bool
    performanceClaimEligible: bool

    @classmethod
    def for_stage(cls, stage: str, scenario_class: str) -> "PilotEvidenceClassificationV1":
        if stage == "P9-A":
            return cls(True, PilotPhaseV1.P9_A_SMOKE_ONLY, scenario_class, False, False)
        if stage in {"P9-B", "P9-C", "P9-D"}:
            return cls(True, stage.replace("-", "_"), scenario_class, False, False)
        if stage == "DEVELOPMENT_ONLY":
            return cls(False, PilotPhaseV1.DEVELOPMENT_ONLY, scenario_class, False, False)
        raise ValueError("UNKNOWN_PILOT_EVIDENCE_STAGE")

    @classmethod
    def from_dict(cls, value: dict) -> "PilotEvidenceClassificationV1":
        expected = {
            "pilotOnly", "pilotPhase", "scenarioClass",
            "formalResultEligible", "performanceClaimEligible",
        }
        if type(value) is not dict or set(value) != expected:
            raise ValueError("STRICT_PILOT_CLASSIFICATION_FIELDS")
        result = cls(**value)
        if type(result.pilotOnly) is not bool or type(result.formalResultEligible) is not bool \
                or type(result.performanceClaimEligible) is not bool:
            raise ValueError("INVALID_PILOT_CLASSIFICATION_TYPES")
        return result

    def to_dict(self) -> dict:
        value = asdict(self)
        value["pilotPhase"] = str(self.pilotPhase)
        return value

    def labels(self) -> tuple[str, ...]:
        if self.pilotPhase == PilotPhaseV1.DEVELOPMENT_ONLY:
            return (
                "DEVELOPMENT_ONLY", "NOT_PILOT_EVIDENCE",
                "NOT_FOR_STATISTICS", "NOT_FOR_THESIS_RESULTS",
            )
        labels = ["PILOT_ONLY", str(self.pilotPhase)]
        if not self.formalResultEligible:
            labels.append("NOT_FOR_FORMAL_THESIS_RESULTS")
        if not self.performanceClaimEligible:
            labels.append("NOT_FOR_PERFORMANCE_CLAIMS")
        return tuple(labels)

    def validate_for_stage(self, stage: str) -> None:
        expected = self.for_stage(stage, self.scenarioClass)
        if self != expected:
            raise ValueError("PILOT_EVIDENCE_CLASSIFICATION_MISMATCH")


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


@dataclass(frozen=True)
class P9AAcceptanceDecisionV1:
    accepted: bool
    errors: tuple[str, ...]
    plannedRunCount: int
    actualRunCount: int
    validRunCount: int

    @classmethod
    def evaluate(
        cls, *, planned: int, actual: int, valid: int,
        classification_errors: int = 0, phase_errors: int = 0,
        raw_sha_errors: int = 0, mirror_sha_errors: int = 0,
        database_invariant_violations: int = 0,
        chain_invariant_violations: int = 0, material_release_errors: int = 0,
        duplicate_errors: int = 0, true_secret: int = 0,
        unclassified: int = 0, formal_mix_errors: int = 0,
        fatal: int = 0, major: int = 0,
    ) -> "P9AAcceptanceDecisionV1":
        checks = {
            "PLANNED_RUN_COUNT": planned == 8,
            "ACTUAL_RUN_COUNT": actual == 8,
            "VALID_RUN_COUNT": valid == 8,
            "CLASSIFICATION": classification_errors == 0,
            "PHASE": phase_errors == 0,
            "RAW_SHA": raw_sha_errors == 0,
            "MIRROR_SHA": mirror_sha_errors == 0,
            "DATABASE_INVARIANTS": database_invariant_violations == 0,
            "CHAIN_INVARIANTS": chain_invariant_violations == 0,
            "MATERIAL_RELEASE": material_release_errors == 0,
            "DUPLICATES": duplicate_errors == 0,
            "TRUE_SECRET": true_secret == 0,
            "UNCLASSIFIED": unclassified == 0,
            "FORMAL_MIX": formal_mix_errors == 0,
            "FATAL": fatal == 0,
            "MAJOR": major == 0,
        }
        errors = tuple(name for name, passed in checks.items() if not passed)
        return cls(not errors, errors, planned, actual, valid)

    def to_dict(self) -> dict:
        value = asdict(self)
        value["errors"] = list(self.errors)
        return value


class P9ADryRunAcceptanceV1:
    @staticmethod
    def evaluate_cases() -> dict[str, P9AAcceptanceDecisionV1]:
        return {
            "eightBusinessPassMissingSmoke": P9AAcceptanceDecisionV1.evaluate(
                planned=8, actual=8, valid=0, classification_errors=8
            ),
            "eightBusinessPassA7MaterialConflict": P9AAcceptanceDecisionV1.evaluate(
                planned=8, actual=8, valid=7, material_release_errors=1
            ),
            "eightValid": P9AAcceptanceDecisionV1.evaluate(
                planned=8, actual=8, valid=8
            ),
            "a6ExpectedFailClosedValid": P9AAcceptanceDecisionV1.evaluate(
                planned=8, actual=8, valid=8
            ),
        }


def validate_run_evidence(run_root: Path, expected_stage: str) -> tuple[str, ...]:
    errors: list[str] = []
    required = ("config.json", "run-state.json", "material-release-evidence.json")
    try:
        records = {name: json.loads((run_root / name).read_text("utf-8")) for name in required}
    except (OSError, json.JSONDecodeError) as exc:
        return (f"EVIDENCE_READ:{type(exc).__name__}",)
    classifications: list[PilotEvidenceClassificationV1] = []
    for name in ("config.json", "run-state.json"):
        try:
            classification = PilotEvidenceClassificationV1.from_dict(
                records[name]["evidenceClassification"]
            )
            classification.validate_for_stage(expected_stage)
            if tuple(records[name].get("classification", ())) != classification.labels():
                errors.append(f"{name}:CLASSIFICATION_LABEL_MISMATCH")
            classifications.append(classification)
        except (KeyError, TypeError, ValueError) as exc:
            errors.append(f"{name}:CLASSIFICATION:{exc}")
    if len(classifications) == 2 and classifications[0] != classifications[1]:
        errors.append("CLASSIFICATION_CONFLICT")
    try:
        nested = PilotEvidenceClassificationV1.from_dict(
            records["config.json"]["config"]["evidenceClassification"]
        )
        if not classifications or nested != classifications[0]:
            errors.append("CONFIG_NESTED_CLASSIFICATION_CONFLICT")
    except (KeyError, TypeError, ValueError) as exc:
        errors.append(f"config.json:NESTED_CLASSIFICATION:{exc}")
    material_record = records["material-release-evidence.json"]
    try:
        authoritative = MaterialReleaseEvidenceV2.from_dict(material_record["current"])
        history = tuple(MaterialReleaseEvidenceV2.from_dict(x) for x in material_record["history"])
        if not history or history[-1] != authoritative:
            errors.append("MATERIAL_RELEASE_HISTORY_TERMINAL_MISMATCH")
        scenario = material_record.get("scenarioProjection")
        final = material_record.get("finalEnvelopeProjection")
        if scenario != authoritative.to_dict() or final != authoritative.to_dict():
            errors.append("MATERIAL_RELEASE_PROJECTION_CONFLICT")
    except (KeyError, TypeError, ValueError) as exc:
        errors.append(f"MATERIAL_RELEASE:{exc}")
    if expected_stage == "P9-D":
        try:
            fault = json.loads((run_root / "fault-evidence.json").read_text("utf-8"))
            required_fault_fields = (
                "runId", "faultId", "faultClass", "scenario", "repeat", "seed",
                "expectedOutcome", "actualOutcome", "expectedRecoveryDisposition",
                "actualRecoveryDisposition", "expectedMaterialDecision",
                "actualMaterialDecision", "injectionRequested", "injectionStartedAt",
                "injectionObserved", "observationAt", "injectionEvidence",
                "observationEvidence", "affectedComponent", "cleanupRequested",
                "cleanupCompleted",
            )
            for field in required_fault_fields:
                if field not in fault or fault[field] in (None, ""):
                    errors.append(f"FAULT_EVIDENCE_MISSING:{field}")
            if fault.get("injectionRequested") is not True:
                errors.append("FAULT_INJECTION_NOT_REQUESTED")
            if fault.get("injectionObserved") is not True or fault.get("observed") is not True:
                errors.append("FAULT_INDEPENDENT_OBSERVATION_MISSING")
            if fault.get("injectionEvidence") == fault.get("observationEvidence"):
                errors.append("FAULT_INJECTION_OBSERVATION_NOT_INDEPENDENT")
            if fault.get("observationSource") in {"controlled-sentinel", "invalid-loopback-port"}:
                errors.append("FAULT_LEGACY_SENTINEL_OBSERVATION")
            if fault.get("runId") != records["config.json"].get("runId"):
                errors.append("FAULT_RUN_ID_MISMATCH")
            if fault.get("actualOutcome") != fault.get("expectedOutcome"):
                errors.append("FAULT_OUTCOME_MISMATCH")
        except (OSError, json.JSONDecodeError, TypeError) as exc:
            errors.append(f"FAULT_EVIDENCE_READ:{type(exc).__name__}")
    return tuple(errors)


def validate_p9a_run_evidence(run_root: Path) -> tuple[str, ...]:
    return validate_run_evidence(run_root, "P9-A")
