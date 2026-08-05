CREATE TYPE r3_control.replica_status AS ENUM (
 'PENDING','ADDING','ADDED','READBACK_VERIFIED','PINNED',
 'FAILED','MISSING','CORRUPT','SUPERSEDED'
);
CREATE TYPE r3_control.replica_verification_status AS ENUM (
 'UNVERIFIED','DIGEST_VERIFIED','OBJECT_VERIFIED','FAILED'
);

CREATE TABLE r3_control.storage_replica (
 storage_replica_id uuid PRIMARY KEY,
 storage_object_digest r3_control.bytes32 NOT NULL
   REFERENCES r3_control.storage_object(object_digest),
 backend text NOT NULL CHECK (backend='IPFS_KUBO'),
 cid text NOT NULL UNIQUE CHECK (cid ~ '^b[a-z2-7]{58}$'),
 cid_version integer NOT NULL CHECK (cid_version=1),
 multihash_code integer NOT NULL CHECK (multihash_code=18),
 codec integer NOT NULL CHECK (codec IN (85,112)),
 chunker_profile text NOT NULL,
 pin_status boolean NOT NULL DEFAULT false,
 replication_status r3_control.replica_status NOT NULL,
 verification_status r3_control.replica_verification_status NOT NULL,
 verified_at timestamptz,
 kubo_node_id text NOT NULL,
 last_error_code text,
 last_error_summary text CHECK (length(last_error_summary)<=512),
 created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
 updated_at timestamptz NOT NULL DEFAULT clock_timestamp(),
 UNIQUE(storage_object_digest,backend),
 CHECK ((verification_status IN ('DIGEST_VERIFIED','OBJECT_VERIFIED'))=(verified_at IS NOT NULL)),
 CHECK (replication_status <> 'PINNED' OR
        (pin_status AND verification_status='OBJECT_VERIFIED')),
 CHECK (pin_status=false OR replication_status='PINNED')
);
