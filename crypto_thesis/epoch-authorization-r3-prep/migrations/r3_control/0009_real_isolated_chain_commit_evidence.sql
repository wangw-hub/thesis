ALTER TYPE r3_control.commit_status ADD VALUE IF NOT EXISTS 'SUBMITTED_REAL_CHAIN';
ALTER TYPE r3_control.commit_status ADD VALUE IF NOT EXISTS 'CONFIRMED_REAL_CHAIN';
ALTER TYPE r3_control.commit_status ADD VALUE IF NOT EXISTS 'FAILED_REAL_CHAIN';

ALTER TABLE r3_control.commit_attempt
 DROP CONSTRAINT commit_attempt_evidence_source_check,
 ADD CONSTRAINT commit_attempt_evidence_source_check
   CHECK (evidence_source IN ('TEST_DOUBLE_ONLY','REAL_ISOLATED_CHAIN_ONLY')),
 ADD COLUMN transaction_nonce bigint CHECK (transaction_nonce >= 0),
 ADD COLUMN block_number bigint CHECK (block_number >= 0),
 ADD COLUMN block_hash r3_control.bytes32,
 ADD COLUMN receipt_status integer CHECK (receipt_status IN (0,1));

ALTER TABLE r3_control.recovery_audit
 DROP CONSTRAINT recovery_audit_evidence_source_check,
 ADD CONSTRAINT recovery_audit_evidence_source_check
   CHECK (evidence_source IN (
     'DATABASE','SYNTHETIC_TEST_FIXTURE','TEST_DOUBLE_ONLY','REAL_ISOLATED_CHAIN_ONLY'
   ));
