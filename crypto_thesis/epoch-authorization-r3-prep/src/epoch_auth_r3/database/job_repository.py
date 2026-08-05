from __future__ import annotations
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from .exceptions import ConflictingDuplicateError, InvalidTransition, StaleWriteRejected
from .models import InsertResult, JobStatus, SyntheticRevocationEventV1
from .operation_id import operation_id_v1

LEGAL = {
    JobStatus.PENDING: {JobStatus.CLAIMED},
    JobStatus.CLAIMED: {JobStatus.CANDIDATE_STORED, JobStatus.RETRY_WAIT, JobStatus.FAILED_TERMINAL, JobStatus.PENDING},
    JobStatus.CANDIDATE_STORED: {JobStatus.READY_FOR_CHAIN_COMMIT},
    JobStatus.READY_FOR_CHAIN_COMMIT: {JobStatus.COMMIT_UNKNOWN, JobStatus.COMMITTED},
    JobStatus.COMMIT_UNKNOWN: {JobStatus.COMMITTED, JobStatus.RETRY_WAIT},
    JobStatus.RETRY_WAIT: {JobStatus.CLAIMED},
    JobStatus.FAILED_TERMINAL: {JobStatus.DEAD_LETTER},
}

EVENT_COLUMNS = (
    "chain_id","authorization_contract","header_registry","event_signature",
    "event_tx_hash","event_log_index","event_block_number","event_block_hash",
    "resource_id","target_epoch","target_state_version","target_header_version",
    "target_key_version",
)


class JobRepository:
    def __init__(self, conn):
        self.conn = conn

    def insert_event(self, event: SyntheticRevocationEventV1, *, max_attempts: int = 3):
        op = operation_id_v1(event)
        values = (
            event.chain_id,event.authorization_contract,event.header_registry,
            event.event_signature,event.tx_hash,event.log_index,event.block_number,
            event.block_hash,event.resource_id,event.new_epoch,event.new_state_version,
            event.new_header_version,event.new_key_version,
        )
        with self.conn.transaction():
            row = self.conn.execute(
                """INSERT INTO r3_control.header_update_job
                   (job_id,operation_id,chain_id,authorization_contract,header_registry,
                    event_signature,event_tx_hash,event_log_index,event_block_number,
                    event_block_hash,resource_id,target_epoch,target_state_version,
                    target_header_version,target_key_version,max_attempts)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                   ON CONFLICT (operation_id) DO NOTHING RETURNING job_id""",
                (uuid4(),op,*values,max_attempts),
            ).fetchone()
            if row:
                return InsertResult.CREATED, row[0], op
            existing = self.conn.execute(
                "SELECT job_id," + ",".join(EVENT_COLUMNS) +
                " FROM r3_control.header_update_job WHERE operation_id=%s FOR UPDATE",
                (op,),
            ).fetchone()
            if tuple(existing[1:]) != values:
                raise ConflictingDuplicateError("operation id fields differ")
            return InsertResult.EXISTING_IDENTICAL, existing[0], op

    def claim_jobs(self, worker_id: str, limit: int, lease_seconds: int):
        if not worker_id or not 1 <= limit <= 100 or not 1 <= lease_seconds <= 3600:
            raise ValueError("invalid claim arguments")
        with self.conn.transaction():
            return self.conn.execute(
                """WITH picked AS (
                     SELECT job_id FROM r3_control.header_update_job
                     WHERE status IN ('PENDING','RETRY_WAIT')
                       AND available_at <= clock_timestamp()
                     ORDER BY available_at, operation_id
                     FOR UPDATE SKIP LOCKED LIMIT %s
                   )
                   UPDATE r3_control.header_update_job j
                      SET status='CLAIMED', lease_owner=%s,
                          lease_expires_at=clock_timestamp()+(%s*interval '1 second'),
                          attempt_count=attempt_count+1,row_version=row_version+1,
                          updated_at=clock_timestamp()
                     FROM picked WHERE j.job_id=picked.job_id
                   RETURNING j.job_id,j.operation_id,j.row_version,j.lease_expires_at""",
                (limit,worker_id,lease_seconds),
            ).fetchall()

    def cas(self, job_id, expected: JobStatus, version: int, new: JobStatus, **fields):
        if new not in LEGAL.get(expected, set()):
            raise InvalidTransition(f"{expected}->{new}")
        assignments = ["status=%s","row_version=row_version+1","updated_at=clock_timestamp()"]
        params: list[object] = [new.value]
        allowed = {
            "candidate_header_digest","candidate_header_object_digest",
            "last_error_code","last_error_summary","available_at","completed_at",
            "lease_owner","lease_expires_at",
        }
        for key, value in fields.items():
            if key not in allowed:
                raise ValueError(key)
            assignments.append(f"{key}=%s")
            params.append(value)
        if new != JobStatus.CLAIMED:
            assignments += ["lease_owner=NULL","lease_expires_at=NULL"]
        if new == JobStatus.COMMITTED:
            assignments.append("completed_at=COALESCE(completed_at,clock_timestamp())")
            proof = self.conn.execute(
                """SELECT 1 FROM r3_control.commit_attempt
                   WHERE job_id=%s AND (
                     (status='CONFIRMED_TEST_DOUBLE' AND evidence_source='TEST_DOUBLE_ONLY')
                     OR
                     (status='CONFIRMED_REAL_CHAIN'
                       AND evidence_source='REAL_ISOLATED_CHAIN_ONLY'
                       AND receipt_status=1 AND block_number IS NOT NULL
                       AND block_hash IS NOT NULL)
                   )""",(job_id,)
            ).fetchone()
            if not proof:
                raise InvalidTransition("COMMITTED requires confirmed commit evidence")
        params += [job_id,expected.value,version]
        with self.conn.transaction():
            row = self.conn.execute(
                f"""UPDATE r3_control.header_update_job SET {','.join(assignments)}
                    WHERE job_id=%s AND status=%s AND row_version=%s
                    RETURNING row_version""", params,
            ).fetchone()
            if not row:
                raise StaleWriteRejected("CAS rejected")
            return row[0]

    def renew_lease(self, job_id, worker_id: str, version: int, seconds: int):
        with self.conn.transaction():
            row = self.conn.execute(
                """UPDATE r3_control.header_update_job
                   SET lease_expires_at=clock_timestamp()+(%s*interval '1 second'),
                       row_version=row_version+1,updated_at=clock_timestamp()
                   WHERE job_id=%s AND status='CLAIMED' AND lease_owner=%s
                     AND row_version=%s AND lease_expires_at>clock_timestamp()
                   RETURNING row_version""",(seconds,job_id,worker_id,version)
            ).fetchone()
            if not row:
                raise StaleWriteRejected("lease renewal rejected")
            return row[0]

    def recover_expired(self, actor: str = "recovery-worker"):
        with self.conn.transaction():
            rows = self.conn.execute(
                """UPDATE r3_control.header_update_job
                   SET status='PENDING',lease_owner=NULL,lease_expires_at=NULL,
                       row_version=row_version+1,updated_at=clock_timestamp(),
                       last_error_code='LEASE_EXPIRED'
                   WHERE status='CLAIMED' AND lease_expires_at<=clock_timestamp()
                   RETURNING job_id""",
            ).fetchall()
            for (job_id,) in rows:
                self.conn.execute(
                    """INSERT INTO r3_control.recovery_audit
                       (audit_id,job_id,action,before_status,after_status,reason_code,evidence_source,actor)
                       VALUES (%s,%s,'LEASE_RECOVERY','CLAIMED','PENDING','LEASE_EXPIRED','DATABASE',%s)""",
                    (uuid4(),job_id,actor),
                )
            return [row[0] for row in rows]

    @staticmethod
    def retry_delay(attempt_count: int, cap_seconds: int = 300) -> int:
        return min(cap_seconds, 2 ** max(0, attempt_count - 1))

    def dead_letter(self, job_id, version: int, code: str, summary: str):
        with self.conn.transaction():
            row = self.conn.execute(
                """UPDATE r3_control.header_update_job
                   SET status='DEAD_LETTER',row_version=row_version+1,
                       updated_at=clock_timestamp()
                   WHERE job_id=%s AND status='FAILED_TERMINAL' AND row_version=%s
                   RETURNING operation_id,row_version""",(job_id,version)
            ).fetchone()
            if not row:
                raise StaleWriteRejected("dead-letter CAS rejected")
            self.conn.execute(
                """INSERT INTO r3_control.dead_letter_job
                   (dead_letter_id,job_id,operation_id,terminal_error_code,
                    terminal_error_summary,original_status)
                   VALUES (%s,%s,%s,%s,%s,'FAILED_TERMINAL')""",
                (uuid4(),job_id,row[0],code,summary),
            )
            return row[1]
