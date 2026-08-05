from dataclasses import dataclass
from enum import StrEnum


class HeaderUpdateKind(StrEnum):
    HEADER_ONLY = "HEADER_ONLY"
    BODY_ROTATION = "BODY_ROTATION"
    NO_NEW_HEADER = "NO_NEW_HEADER"
    POLICY_DECISION_REQUIRED = "POLICY_DECISION_REQUIRED"


@dataclass(frozen=True)
class HeaderUpdateDecision:
    kind: HeaderUpdateKind
    reason: str


def decide_update(
    event_name: str,
    *,
    resource_status: str = "ACTIVE",
    ck_compromised: bool = False,
    body_changed: bool = False,
) -> HeaderUpdateDecision:
    if resource_status == "REVOKED":
        return HeaderUpdateDecision(HeaderUpdateKind.NO_NEW_HEADER, "RESOURCE_TERMINATED")
    if ck_compromised or body_changed:
        return HeaderUpdateDecision(HeaderUpdateKind.BODY_ROTATION, "NEW_BODY_AND_CK_REQUIRED")
    if event_name in {
        "PolicyUpdated",
        "EpochAdvanced",
        "ResourceStatusChanged",
        "UserKeyRotated",
        "UserStatusChanged",
    }:
        return HeaderUpdateDecision(HeaderUpdateKind.HEADER_ONLY, "RECIPIENT_OR_AUTH_STATE_CHANGED")
    return HeaderUpdateDecision(HeaderUpdateKind.POLICY_DECISION_REQUIRED, "UNCLASSIFIED_TRIGGER")
