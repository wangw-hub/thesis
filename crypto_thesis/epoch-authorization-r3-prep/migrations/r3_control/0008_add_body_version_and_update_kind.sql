CREATE TYPE r3_control.header_update_kind AS ENUM (
 'INITIAL','HEADER_ONLY','BODY_ROTATION'
);

ALTER TABLE r3_control.header_version
 ADD COLUMN body_version bigint,
 ADD COLUMN update_kind r3_control.header_update_kind,
 ADD COLUMN body_object_digest r3_control.bytes32 REFERENCES r3_control.storage_object(object_digest);

UPDATE r3_control.header_version
 SET body_version=key_version;

UPDATE r3_control.header_version current_header
 SET update_kind = CASE
   WHEN current_header.header_version=1 THEN 'INITIAL'::r3_control.header_update_kind
   WHEN current_header.key_version = (
     SELECT previous_header.key_version FROM r3_control.header_version previous_header
      WHERE previous_header.resource_id=current_header.resource_id
        AND previous_header.header_version=current_header.header_version-1
   ) THEN 'HEADER_ONLY'::r3_control.header_update_kind
   ELSE 'BODY_ROTATION'::r3_control.header_update_kind
 END;

ALTER TABLE r3_control.header_version
 ALTER COLUMN body_version SET NOT NULL,
 ALTER COLUMN update_kind SET NOT NULL,
 ADD CONSTRAINT header_body_version_positive CHECK (body_version >= 1),
 ADD CONSTRAINT header_key_equals_body_version CHECK (key_version = body_version);

CREATE FUNCTION r3_control.guard_header_update_kind() RETURNS trigger
LANGUAGE plpgsql AS $$
DECLARE
 prior_body_version bigint;
 prior_key_version bigint;
 prior_body_digest bytea;
BEGIN
 IF NEW.body_object_digest IS NULL THEN
   RAISE EXCEPTION 'new header version requires a body object digest' USING ERRCODE='23514';
 END IF;
 IF NEW.header_version=1 THEN
   IF NEW.update_kind<>'INITIAL' OR NEW.body_version<>1 OR NEW.key_version<>1
      OR NEW.previous_header_digest IS NOT NULL THEN
     RAISE EXCEPTION 'invalid INITIAL header transition' USING ERRCODE='23514';
   END IF;
   RETURN NEW;
 END IF;

 SELECT body_version,key_version,body_object_digest
   INTO prior_body_version,prior_key_version,prior_body_digest
   FROM r3_control.header_version
  WHERE resource_id=NEW.resource_id AND header_version=NEW.header_version-1;
 IF prior_body_version IS NULL THEN
   RAISE EXCEPTION 'missing previous header version' USING ERRCODE='23514';
 END IF;
 IF NEW.update_kind='HEADER_ONLY' THEN
   IF NEW.body_version<>prior_body_version OR NEW.key_version<>prior_key_version
      OR prior_body_digest IS NULL OR NEW.body_object_digest<>prior_body_digest THEN
     RAISE EXCEPTION 'invalid HEADER_ONLY transition' USING ERRCODE='23514';
   END IF;
 ELSIF NEW.update_kind='BODY_ROTATION' THEN
   IF NEW.body_version<>prior_body_version+1 OR NEW.key_version<>prior_key_version+1
      OR prior_body_digest IS NULL OR NEW.body_object_digest=prior_body_digest THEN
     RAISE EXCEPTION 'invalid BODY_ROTATION transition' USING ERRCODE='23514';
   END IF;
 ELSE
   RAISE EXCEPTION 'INITIAL is only valid for header version 1' USING ERRCODE='23514';
 END IF;
 RETURN NEW;
END $$;

CREATE TRIGGER header_update_kind_guard
 BEFORE INSERT ON r3_control.header_version
 FOR EACH ROW EXECUTE FUNCTION r3_control.guard_header_update_kind();
