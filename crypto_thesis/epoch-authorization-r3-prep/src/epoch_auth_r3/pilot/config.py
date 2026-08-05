from __future__ import annotations

import hashlib
from dataclasses import dataclass, field, fields

from epoch_auth_r3.serialization.jcs_adapter import canonicalize
from epoch_auth_r3.pilot.attempt import PilotAttemptIdV1
from epoch_auth_r3.pilot.p9a_evidence_contract import PilotEvidenceClassificationV1

DOMAIN = b"EPOCH_AUTH_R3_I9_PILOT_RUN_V1\x00"
CONFIG_DOMAIN = b"EPOCH_AUTH_R3_I9_PILOT_CONFIG_V1\x00"
ATTEMPT_RUN_DOMAIN = b"EPOCH_AUTH_R3_I9_PILOT_RUN_ATTEMPT_V1\x00"


@dataclass(frozen=True)
class R3PilotConfigV1:
    schemaVersion: int
    pilotProtocolVersion: str
    pilotRunGroupId: str
    seed: int
    workloadId: str
    scenarioClass: str
    updateKind: str
    bodySizeBytes: int
    recipientCount: int
    affectedResourceCount: int
    workerCount: int
    storageMode: str
    faultScenario: str
    repeatIndex: int
    warmup: bool
    measurementEnabled: bool
    chainId: int
    authorizationStateAddress: str
    headerRegistryAddress: str
    databaseName: str
    localObjectStoreRoot: str
    kuboApi: str
    kuboAddProfileDigest: str
    softwareCommit: str
    environmentManifestDigest: str
    createdAt: str
    evidenceClassification: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.schemaVersion != 1 or self.pilotProtocolVersion != "I9_PILOT_V1":
            raise ValueError("UNSUPPORTED_PILOT_CONFIG")
        for name in ("seed", "bodySizeBytes", "recipientCount", "affectedResourceCount",
                     "workerCount", "repeatIndex", "chainId"):
            if type(getattr(self, name)) is not int or getattr(self, name) < 0:
                raise ValueError(f"INVALID_{name.upper()}")
        if self.databaseName != "epoch_auth_r3_i9_pilot":
            raise ValueError("NON_PILOT_DATABASE")
        expected_prefix = (
            "R3_I9_DEVELOPMENT_ONLY"
            if self.pilotRunGroupId == "DEVELOPMENT_ONLY"
            else "R3_I9_PILOT_ONLY"
        )
        if not self.workloadId.startswith(expected_prefix):
            raise ValueError("INVALID_EXECUTION_NAMESPACE")
        if self.evidenceClassification:
            classification = PilotEvidenceClassificationV1.from_dict(
                self.evidenceClassification
            )
            classification.validate_for_stage(self.pilotRunGroupId)
            if classification.scenarioClass != self.scenarioClass:
                raise ValueError("CONFIG_CLASSIFICATION_SCENARIO_MISMATCH")

    def identity_dict(self) -> dict:
        value = {f.name: getattr(self, f.name) for f in fields(self)}
        value.pop("createdAt")
        return value

    def canonical_bytes(self) -> bytes:
        return canonicalize(self.identity_dict())

    @classmethod
    def from_strict_dict(cls, value: dict) -> "R3PilotConfigV1":
        expected = {f.name for f in fields(cls)}
        if type(value) is not dict or set(value) != expected:
            raise ValueError("STRICT_CONFIG_FIELDS")
        return cls(**value)


def deterministic_run_id(config: R3PilotConfigV1) -> str:
    return hashlib.sha256(DOMAIN + config.canonical_bytes()).hexdigest()


def config_digest(config: R3PilotConfigV1) -> str:
    return hashlib.sha256(CONFIG_DOMAIN + config.canonical_bytes()).hexdigest()


def attempt_scoped_run_id(
    attempt_id: str, config: R3PilotConfigV1, execution_attempt_ordinal: int = 0
) -> str:
    attempt_id = PilotAttemptIdV1.validate(attempt_id).serialize()
    if type(execution_attempt_ordinal) is not int or execution_attempt_ordinal < 0:
        raise ValueError("INVALID_EXECUTION_ATTEMPT_ORDINAL")
    material = (
        ATTEMPT_RUN_DOMAIN
        + attempt_id.encode("ascii")
        + bytes.fromhex(config_digest(config))
        + execution_attempt_ordinal.to_bytes(4, "big")
    )
    return hashlib.sha256(material).hexdigest()


def validate_remote_authoritative_config(config: R3PilotConfigV1, attempt_id: str) -> None:
    root = config.localObjectStoreRoot
    forbidden = ("\\", "d:", "c:", "${", "%temp%", "sandbox")
    if any(token in root.lower() for token in forbidden):
        raise ValueError("WINDOWS_OR_UNRESOLVED_PATH")
    expected = f"/var/lib/epoch-auth-r3/i9-pilot/attempts/{attempt_id}/local-store"
    if root != expected:
        raise ValueError("NON_REMOTE_AUTHORITATIVE_ROOT")
