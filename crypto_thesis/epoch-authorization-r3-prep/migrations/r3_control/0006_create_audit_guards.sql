CREATE FUNCTION r3_control.reject_audit_mutation() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
 RAISE EXCEPTION 'recovery_audit is append-only' USING ERRCODE='55000';
END $$;
CREATE TRIGGER recovery_audit_no_update_delete
 BEFORE UPDATE OR DELETE ON r3_control.recovery_audit
 FOR EACH ROW EXECUTE FUNCTION r3_control.reject_audit_mutation();
