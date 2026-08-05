CREATE FUNCTION r3_control.guard_job_transition() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
 IF NEW.status <> OLD.status AND NOT (
   (OLD.status='PENDING' AND NEW.status='CLAIMED') OR
   (OLD.status='CLAIMED' AND NEW.status IN ('CANDIDATE_STORED','RETRY_WAIT','FAILED_TERMINAL')) OR
   (OLD.status='CANDIDATE_STORED' AND NEW.status='READY_FOR_CHAIN_COMMIT') OR
   (OLD.status='READY_FOR_CHAIN_COMMIT' AND NEW.status IN ('COMMIT_UNKNOWN','COMMITTED')) OR
   (OLD.status='COMMIT_UNKNOWN' AND NEW.status IN ('COMMITTED','RETRY_WAIT')) OR
   (OLD.status='RETRY_WAIT' AND NEW.status='CLAIMED') OR
   (OLD.status='FAILED_TERMINAL' AND NEW.status='DEAD_LETTER') OR
   (OLD.status='CLAIMED' AND NEW.status='PENDING')
 ) THEN RAISE EXCEPTION 'illegal job transition % -> %', OLD.status, NEW.status
   USING ERRCODE='23514';
 END IF;
 IF NEW.row_version <> OLD.row_version + 1 THEN
   RAISE EXCEPTION 'row_version must increment by one' USING ERRCODE='23514';
 END IF;
 RETURN NEW;
END $$;
CREATE TRIGGER header_update_job_transition_guard
 BEFORE UPDATE ON r3_control.header_update_job
 FOR EACH ROW EXECUTE FUNCTION r3_control.guard_job_transition();

CREATE FUNCTION r3_control.guard_header_continuity() RETURNS trigger
LANGUAGE plpgsql AS $$
DECLARE prior_digest bytea;
BEGIN
 IF NEW.header_version > 1 THEN
   SELECT header_digest INTO prior_digest FROM r3_control.header_version
    WHERE resource_id=NEW.resource_id AND header_version=NEW.header_version-1;
   IF prior_digest IS NULL OR prior_digest <> NEW.previous_header_digest THEN
     RAISE EXCEPTION 'previous header digest discontinuity' USING ERRCODE='23514';
   END IF;
 END IF;
 RETURN NEW;
END $$;
CREATE TRIGGER header_version_continuity_guard
 BEFORE INSERT ON r3_control.header_version
 FOR EACH ROW EXECUTE FUNCTION r3_control.guard_header_continuity();
