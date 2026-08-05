from dataclasses import dataclass
from enum import StrEnum


class ReleaseDecision(StrEnum):
    ALLOW = "ALLOW"
    HEADER_UPDATE_PENDING = "HEADER_UPDATE_PENDING"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class AccessMaterialReleaseGuard:
    def evaluate(self, composite_state, *, header_object_valid: bool) -> ReleaseDecision:
        if composite_state is None:
            return ReleaseDecision.UNKNOWN
        if hasattr(composite_state, "consistency_class"):
            consistency = composite_state.consistency_class
            if consistency.value == "AUTHORIZATION_AHEAD_OF_HEADER":
                return ReleaseDecision.HEADER_UPDATE_PENDING
            if consistency.value != "CONSISTENT":
                return ReleaseDecision.UNKNOWN
            return ReleaseDecision.ALLOW if header_object_valid else ReleaseDecision.UNKNOWN
        auth = composite_state.authorization
        anchor = composite_state.header
        if (
            auth.policy_digest != anchor.policy_digest
            or auth.epoch != anchor.epoch
            or auth.state_version != anchor.state_version
        ):
            return ReleaseDecision.HEADER_UPDATE_PENDING
        return ReleaseDecision.ALLOW if header_object_valid else ReleaseDecision.UNKNOWN
