CREATE TYPE r3_control.authorization_event_status AS ENUM
 ('OBSERVED','RESOLVED','JOBS_CREATED','SUPERSEDED','AUDIT_ONLY','REJECTED');

CREATE TABLE r3_control.authorization_event (
 event_id uuid PRIMARY KEY,
 chain_id bigint NOT NULL,
 authorization_contract r3_control.bytes20 NOT NULL,
 event_name text NOT NULL,
 event_signature r3_control.bytes32 NOT NULL,
 transaction_hash r3_control.bytes32 NOT NULL,
 log_index integer NOT NULL CHECK (log_index >= 0),
 block_number bigint NOT NULL CHECK (block_number >= 0),
 block_hash r3_control.bytes32 NOT NULL,
 event_class text NOT NULL CHECK (event_class IN ('DIRECT_RESOURCE','USER_SCOPE','AUDIT_ONLY')),
 resource_id r3_control.bytes32,
 user_id r3_control.bytes32,
 payload jsonb NOT NULL,
 payload_digest r3_control.bytes32 NOT NULL,
 status r3_control.authorization_event_status NOT NULL DEFAULT 'OBSERVED',
 created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
 UNIQUE (chain_id,authorization_contract,transaction_hash,log_index)
);

CREATE FUNCTION r3_control.reject_conflicting_authorization_event() RETURNS trigger
LANGUAGE plpgsql AS $$
DECLARE old_digest bytea; old_hash bytea;
BEGIN
 SELECT payload_digest,block_hash INTO old_digest,old_hash
 FROM r3_control.authorization_event
 WHERE chain_id=NEW.chain_id AND authorization_contract=NEW.authorization_contract
 AND transaction_hash=NEW.transaction_hash AND log_index=NEW.log_index;
 IF old_digest IS NOT NULL AND (old_digest<>NEW.payload_digest OR old_hash<>NEW.block_hash) THEN
   RAISE EXCEPTION 'conflicting duplicate authorization event' USING ERRCODE='23505';
 END IF;
 RETURN NEW;
END $$;
CREATE TRIGGER authorization_event_conflict_guard
 BEFORE INSERT ON r3_control.authorization_event
 FOR EACH ROW EXECUTE FUNCTION r3_control.reject_conflicting_authorization_event();

CREATE TABLE r3_control.resource_recipient_index (
 resource_id r3_control.bytes32 NOT NULL,
 user_id r3_control.bytes32 NOT NULL,
 recipient_key_id r3_control.bytes32 NOT NULL,
 user_version bigint NOT NULL CHECK (user_version > 0),
 active boolean NOT NULL,
 source_header_digest r3_control.bytes32 NOT NULL,
 updated_at timestamptz NOT NULL DEFAULT clock_timestamp(),
 PRIMARY KEY (resource_id,user_id),
 UNIQUE (resource_id,recipient_key_id)
);

CREATE TABLE r3_control.resource_recipient_index_state (
 resource_id r3_control.bytes32 PRIMARY KEY,
 completeness text NOT NULL CHECK (completeness IN ('COMPLETE','INCOMPLETE')),
 source_header_digest r3_control.bytes32,
 updated_at timestamptz NOT NULL DEFAULT clock_timestamp()
);

CREATE TABLE r3_control.content_key_record (
 resource_id r3_control.bytes32 NOT NULL,
 body_version bigint NOT NULL CHECK (body_version > 0),
 key_version bigint NOT NULL CHECK (key_version = body_version),
 protection_key_version bigint NOT NULL CHECK (protection_key_version > 0),
 nonce bytea NOT NULL CHECK (octet_length(nonce)=12),
 ciphertext bytea NOT NULL CHECK (octet_length(ciphertext)=48),
 metadata_digest r3_control.bytes32 NOT NULL,
 record_json jsonb NOT NULL,
 created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
 PRIMARY KEY (resource_id,body_version)
);

CREATE TABLE r3_control.authorization_event_job (
 event_id uuid NOT NULL REFERENCES r3_control.authorization_event(event_id),
 resource_id r3_control.bytes32 NOT NULL,
 job_id uuid NOT NULL REFERENCES r3_control.header_update_job(job_id),
 update_kind r3_control.header_update_kind NOT NULL,
 PRIMARY KEY(event_id,resource_id),
 UNIQUE(job_id)
);
