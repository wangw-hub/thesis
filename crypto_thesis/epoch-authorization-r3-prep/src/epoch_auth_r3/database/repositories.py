from uuid import uuid4


class ArtifactRepository:
    def __init__(self, conn):
        self.conn = conn

    def put_storage_object(self, digest, namespace, kind, size, verified=True):
        with self.conn.transaction():
            return self.conn.execute(
                """INSERT INTO r3_control.storage_object
                   (object_digest,backend,namespace,object_kind,size_bytes,reference_schema_version,verified)
                   VALUES (%s,'local',%s,%s,%s,1,%s)
                   ON CONFLICT (object_digest) DO UPDATE SET
                     updated_at=clock_timestamp()
                   WHERE r3_control.storage_object.namespace=EXCLUDED.namespace
                     AND r3_control.storage_object.object_kind=EXCLUDED.object_kind
                     AND r3_control.storage_object.size_bytes=EXCLUDED.size_bytes
                   RETURNING object_digest""",(digest,namespace,kind,size,verified)
            ).fetchone()

    def add_header(self, job_id, operation_id, resource_id, version, key_version,
                   epoch, state_version, header_digest, previous_digest, object_digest,
                   *, body_version, update_kind, body_object_digest):
        with self.conn.transaction():
            return self.conn.execute(
                """INSERT INTO r3_control.header_version
                   (header_version_id,job_id,operation_id,resource_id,header_version,
                    body_version,key_version,update_kind,epoch,state_version,header_digest,
                    previous_header_digest,header_object_digest,body_object_digest,status)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'STORED')
                   RETURNING header_version_id""",
                (uuid4(),job_id,operation_id,resource_id,version,body_version,key_version,
                 update_kind,epoch,state_version,header_digest,previous_digest,object_digest,
                 body_object_digest),
            ).fetchone()[0]

    def add_commit_attempt(self, job_id, operation_id, number, status="PREPARED"):
        with self.conn.transaction():
            return self.conn.execute(
                """INSERT INTO r3_control.commit_attempt
                   (attempt_id,job_id,operation_id,attempt_number,status,evidence_source)
                   VALUES (%s,%s,%s,%s,%s,'TEST_DOUBLE_ONLY') RETURNING attempt_id""",
                (uuid4(),job_id,operation_id,number,status),
            ).fetchone()[0]

    def set_commit_attempt(self, attempt_id, old_status, new_status):
        allowed = {
            ("PREPARED","BROADCAST_UNKNOWN"),
            ("PREPARED","CONFIRMED_TEST_DOUBLE"),
            ("BROADCAST_UNKNOWN","CONFIRMED_TEST_DOUBLE"),
            ("BROADCAST_UNKNOWN","FAILED_TEST_DOUBLE"),
        }
        if (old_status,new_status) not in allowed:
            raise ValueError("illegal commit transition")
        with self.conn.transaction():
            row = self.conn.execute(
                """UPDATE r3_control.commit_attempt
                   SET status=%s,row_version=row_version+1,updated_at=clock_timestamp()
                   WHERE attempt_id=%s AND status=%s RETURNING row_version""",
                (new_status,attempt_id,old_status),
            ).fetchone()
            if not row:
                raise ValueError("stale commit attempt")
            return row[0]

    def add_real_commit_attempt(self, job_id, operation_id, number, transaction_hash,
                                transaction_nonce):
        with self.conn.transaction():
            return self.conn.execute(
                """INSERT INTO r3_control.commit_attempt
                   (attempt_id,job_id,operation_id,attempt_number,status,evidence_source,
                    transaction_hash,transaction_nonce)
                   VALUES (%s,%s,%s,%s,'SUBMITTED_REAL_CHAIN',
                           'REAL_ISOLATED_CHAIN_ONLY',%s,%s)
                   RETURNING attempt_id""",
                (uuid4(),job_id,operation_id,number,transaction_hash,transaction_nonce),
            ).fetchone()[0]

    def confirm_real_commit(self, attempt_id, block_number, block_hash, receipt_status):
        target = "CONFIRMED_REAL_CHAIN" if receipt_status == 1 else "FAILED_REAL_CHAIN"
        with self.conn.transaction():
            row = self.conn.execute(
                """UPDATE r3_control.commit_attempt
                      SET status=%s,block_number=%s,block_hash=%s,receipt_status=%s,
                          row_version=row_version+1,updated_at=clock_timestamp()
                    WHERE attempt_id=%s AND status='SUBMITTED_REAL_CHAIN'
                      AND evidence_source='REAL_ISOLATED_CHAIN_ONLY'
                    RETURNING row_version""",
                (target,block_number,block_hash,receipt_status,attempt_id),
            ).fetchone()
            if not row:
                raise ValueError("stale real-chain commit attempt")
            return row[0]

    def audit(self, job_id, action, before, after, reason, actor="test"):
        with self.conn.transaction():
            return self.conn.execute(
                """INSERT INTO r3_control.recovery_audit
                   (audit_id,job_id,action,before_status,after_status,reason_code,evidence_source,actor)
                   VALUES (%s,%s,%s,%s,%s,%s,'SYNTHETIC_TEST_FIXTURE',%s)
                   RETURNING audit_id""",
                (uuid4(),job_id,action,before,after,reason,actor),
            ).fetchone()[0]
