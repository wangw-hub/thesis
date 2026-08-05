from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class PilotChainWriteStepV1:
    sequence: int
    targetContract: str
    method: str
    sender: str
    noncePolicy: str


@dataclass(frozen=True)
class PilotChainWritePlanV1:
    attemptId: str
    runId: str
    jobId: str
    resourceId: str
    operationId: str
    expectedTransactionCount: int
    transactionSequence: tuple[PilotChainWriteStepV1, ...]
    requiredPriorDatabaseState: str = "READY_FOR_CHAIN_SUBMISSION"
    requiredPostTransactionVerification: str = "RECEIPT_AND_COMPOSITE_STATE"

    def __post_init__(self) -> None:
        if self.expectedTransactionCount != len(self.transactionSequence):
            raise ValueError("CHAIN_WRITE_PLAN_COUNT_MISMATCH")
        if tuple(step.sequence for step in self.transactionSequence) != tuple(
            range(1, self.expectedTransactionCount + 1)
        ):
            raise ValueError("CHAIN_WRITE_PLAN_SEQUENCE_INVALID")

    def to_dict(self) -> dict:
        return asdict(self)


class PilotChainWriteAdmissionGuardV1:
    @staticmethod
    def admit(
        *, plan: PilotChainWritePlanV1, visibility: dict,
        object_verification: dict, chain_writes_before_admission: int,
    ) -> dict:
        failures = []
        if visibility.get("status") != "READY_FOR_CHAIN_SUBMISSION":
            failures.append("JOB_CREATE_NOT_COMMITTED")
        if not visibility.get("visibleFromIndependentConnection"):
            failures.append("JOB_CREATE_POST_COMMIT_NOT_VISIBLE")
        if not object_verification.get("headerVerified"):
            failures.append("HEADER_OBJECT_NOT_VERIFIED")
        if not object_verification.get("bodyVerified"):
            failures.append("BODY_OBJECT_NOT_VERIFIED")
        if chain_writes_before_admission != 0:
            failures.append("CHAIN_WRITE_BEFORE_JOB_COMMIT")
        if failures:
            raise RuntimeError("CHAIN_WRITE_ADMISSION_REJECTED:" + ",".join(failures))
        return {
            "decision": "ADMITTED", "jobId": plan.jobId,
            "expectedTransactionCount": plan.expectedTransactionCount,
            "chainWritesBeforeAdmission": 0,
        }
