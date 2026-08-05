from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class PilotStageStateV1(StrEnum):
    P9_A_NOT_STARTED = "P9_A_NOT_STARTED"
    P9_A_RUNNING = "P9_A_RUNNING"
    P9_A_FAILED = "P9_A_FAILED"
    P9_A_PASSED = "P9_A_PASSED"
    P9_B_RUNNING = "P9_B_RUNNING"
    P9_B_FAILED = "P9_B_FAILED"
    P9_B_PASSED = "P9_B_PASSED"
    P9_C_RUNNING = "P9_C_RUNNING"
    P9_C_FAILED = "P9_C_FAILED"
    P9_C_PASSED = "P9_C_PASSED"
    P9_D_RUNNING = "P9_D_RUNNING"
    P9_D_FAILED = "P9_D_FAILED"
    P9_D_PASSED = "P9_D_PASSED"
    PILOT_ACCEPTED = "PILOT_ACCEPTED"


_NEXT = {
    PilotStageStateV1.P9_A_NOT_STARTED: PilotStageStateV1.P9_A_RUNNING,
    PilotStageStateV1.P9_A_PASSED: PilotStageStateV1.P9_B_RUNNING,
    PilotStageStateV1.P9_B_PASSED: PilotStageStateV1.P9_C_RUNNING,
    PilotStageStateV1.P9_C_PASSED: PilotStageStateV1.P9_D_RUNNING,
    PilotStageStateV1.P9_D_PASSED: PilotStageStateV1.PILOT_ACCEPTED,
}


def enter_next_stage(current: PilotStageStateV1) -> PilotStageStateV1:
    try:
        return _NEXT[current]
    except KeyError as exc:
        raise ValueError("PILOT_STAGE_GATE_BLOCKED") from exc


@dataclass(frozen=True)
class StageQuality:
    planned: int
    actual: int
    valid: int
    missingPhases: int = 0
    rawShaErrors: int = 0
    databaseInvariantViolations: int = 0
    chainInvariantViolations: int = 0
    incorrectMaterialReleases: int = 0
    duplicateAnchors: int = 0
    duplicateCommitted: int = 0

    def passed(self) -> bool:
        return (
            self.planned == self.actual == self.valid
            and sum((
                self.missingPhases, self.rawShaErrors, self.databaseInvariantViolations,
                self.chainInvariantViolations, self.incorrectMaterialReleases,
                self.duplicateAnchors, self.duplicateCommitted,
            )) == 0
        )
