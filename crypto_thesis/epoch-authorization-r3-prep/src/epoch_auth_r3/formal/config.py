from __future__ import annotations

import hashlib
from dataclasses import dataclass, field, fields

from epoch_auth_r3.serialization.jcs_adapter import canonicalize
from epoch_auth_r3.formal.identity import FormalAttemptIdV1
from epoch_auth_r3.formal.classification import FormalEvidenceClassificationV1


DOMAIN = b"EPOCH_AUTH_R3_FORMAL_RUN_V1\x00"
CONFIG_DOMAIN = b"EPOCH_AUTH_R3_FORMAL_CONFIG_V1\x00"


@dataclass(frozen=True)
class R3FormalConfigV1:
    schemaVersion: int
    formalProtocolVersion: str
    experimentId: str
    seed: int
    workloadId: str
    scenarioClass: str
    semanticClass: str
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
        if self.schemaVersion != 1 or self.formalProtocolVersion != "R3_FORMAL_V1":
            raise ValueError("UNSUPPORTED_FORMAL_CONFIG")
        for name in (
            "seed", "bodySizeBytes", "recipientCount", "affectedResourceCount",
            "workerCount", "repeatIndex", "chainId",
        ):
            if type(getattr(self, name)) is not int or getattr(self, name) < 0:
                raise ValueError(f"INVALID_{name.upper()}")
        if self.databaseName != "epoch_auth_r3_formal":
            raise ValueError("NON_FORMAL_DATABASE")
        if not self.workloadId.startswith("R3_FORMAL_"):
            raise ValueError("INVALID_EXECUTION_NAMESPACE")
        if "PILOT" in self.workloadId or "I9" in self.workloadId:
            raise ValueError("PILOT_IDENTITY_REUSE")
        if self.evidenceClassification:
            classification = FormalEvidenceClassificationV1.from_dict(
                self.evidenceClassification
            )
            if classification.experimentId != self.experimentId:
                raise ValueError("CONFIG_CLASSIFICATION_EXPERIMENT_MISMATCH")

    def identity_dict(self) -> dict:
        value = {f.name: getattr(self, f.name) for f in fields(self)}
        value.pop("createdAt")
        return value

    def canonical_bytes(self) -> bytes:
        return canonicalize(self.identity_dict())

    @classmethod
    def from_strict_dict(cls, value: dict) -> "R3FormalConfigV1":
        expected = {f.name for f in fields(cls)}
        if type(value) is not dict or set(value) != expected:
            raise ValueError("STRICT_CONFIG_FIELDS")
        return cls(**value)


def deterministic_run_id(config: R3FormalConfigV1) -> str:
    return hashlib.sha256(DOMAIN + config.canonical_bytes()).hexdigest()


def config_digest(config: R3FormalConfigV1) -> str:
    return hashlib.sha256(CONFIG_DOMAIN + config.canonical_bytes()).hexdigest()


def validate_remote_authoritative_config(config: R3FormalConfigV1, attempt_id: str) -> None:
    root = config.localObjectStoreRoot
    forbidden = ("\\", "d:", "c:", "${", "%temp%", "sandbox", "i9-pilot")
    if any(token in root.lower() for token in forbidden):
        raise ValueError("WINDOWS_OR_PILOT_PATH")
    expected = f"/var/lib/epoch-auth-r3/formal/attempts/{attempt_id}/local-store"
    if root != expected:
        raise ValueError("NON_REMOTE_AUTHORITATIVE_ROOT")
