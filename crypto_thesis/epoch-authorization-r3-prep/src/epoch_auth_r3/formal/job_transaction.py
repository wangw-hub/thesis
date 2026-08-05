from __future__ import annotations

import json
from dataclasses import asdict, dataclass

from .database import FormalDatabaseConnectionFactoryV1


@dataclass(frozen=True)
class FormalJobCandidateV1:
    attemptId: str
    runId: str
    jobId: str
    resourceId: str
    operationId: str
    updateKind: str
    headerDigest: str
    headerObjectDigest: str
    bodyDigest: str
    bodyObjectDigest: str
    chainWritePlan: dict


class FormalJobCreateTransactionV1:
    @staticmethod
    def create(factory: FormalDatabaseConnectionFactoryV1, value: FormalJobCandidateV1) -> dict:
        with factory.connect() as conn:
            try:
                conn.execute("BEGIN")
                with conn.cursor() as cur:
                    cur.execute("""INSERT INTO r3_formal.formal_run_job
                        (job_id, run_id, attempt_id, status, operation_id,
                         resource_id, update_kind, header_digest,
                         header_object_digest, body_digest, body_object_digest,
                         chain_write_plan)
                        VALUES (%s,%s,%s,'READY_FOR_CHAIN_SUBMISSION',%s,%s,%s,
                                %s,%s,%s,%s,%s::jsonb)""",
                        (
                            value.jobId, value.runId, value.attemptId,
                            value.operationId, value.resourceId, value.updateKind,
                            value.headerDigest, value.headerObjectDigest,
                            value.bodyDigest, value.bodyObjectDigest,
                            json.dumps(value.chainWritePlan, sort_keys=True),
                        ))
                    if cur.rowcount != 1:
                        raise RuntimeError("JOB_CREATE_NOT_COMMITTED")
                conn.commit()
            except Exception:
                conn.rollback()
                raise
        return {"transactionState": "COMMITTED", "candidate": asdict(value)}


class FormalJobVisibilityGateV1:
    @staticmethod
    def verify(factory: FormalDatabaseConnectionFactoryV1, expected: FormalJobCandidateV1) -> dict:
        with factory.connect() as conn:
            with conn.cursor() as cur:
                cur.execute("""SELECT run_id, attempt_id, operation_id, resource_id,
                    update_kind, header_digest, header_object_digest,
                    body_digest, body_object_digest, status
                    FROM r3_formal.formal_run_job WHERE job_id=%s""",
                    (expected.jobId,))
                row = cur.fetchone()
        if row is None:
            raise RuntimeError("JOB_LOOKUP_NOT_FOUND")
        actual = tuple(row)
        wanted = (
            expected.runId, expected.attemptId, expected.operationId,
            expected.resourceId, expected.updateKind, expected.headerDigest,
            expected.headerObjectDigest, expected.bodyDigest,
            expected.bodyObjectDigest, "READY_FOR_CHAIN_SUBMISSION",
        )
        if actual != wanted:
            raise RuntimeError("JOB_STATE_CONFLICT")
        return {
            "visibleFromIndependentConnection": True,
            "status": actual[-1], "jobId": expected.jobId,
        }


class FormalDatabaseFinalizeTransactionV1:
    @staticmethod
    def commit(factory: FormalDatabaseConnectionFactoryV1, job_id: str, run_id: str) -> dict:
        with factory.connect() as conn:
            try:
                conn.execute("BEGIN")
                with conn.cursor() as cur:
                    cur.execute("""UPDATE r3_formal.formal_run_job
                        SET status='COMMITTED', committed_at=clock_timestamp()
                        WHERE job_id=%s AND run_id=%s
                          AND status='READY_FOR_CHAIN_SUBMISSION'""",
                        (job_id, run_id))
                    if cur.rowcount != 1:
                        raise RuntimeError("JOB_STATE_CONFLICT")
                conn.commit()
            except Exception:
                conn.rollback()
                raise
        return {"transactionState": "COMMITTED", "jobState": "COMMITTED"}
