CREATE INDEX header_update_job_claim_idx
 ON r3_control.header_update_job (available_at, operation_id)
 WHERE status IN ('PENDING','RETRY_WAIT');
CREATE INDEX header_update_job_lease_idx
 ON r3_control.header_update_job (lease_expires_at)
 WHERE status = 'CLAIMED';
CREATE UNIQUE INDEX one_committed_header_per_resource
 ON r3_control.header_version (resource_id)
 WHERE status = 'COMMITTED';
CREATE INDEX recovery_audit_job_idx
 ON r3_control.recovery_audit (job_id, created_at, audit_id);
