# Formal Factor and Level Design

Eight factors are retained in `formal-factor-matrix.json`. Frozen levels are deliberately blocked: recipient_count 2/8/32, affected_count 1/4, body_bytes 65536/1048576/8388608, update_kind as a semantic block, replica_state LOCAL_ONLY/KUBO_REPLICA, fault_class NONE/CORRUPT_RESTORE/CID_MISMATCH/BOTH_MISSING, workload_type HEADER_UPDATE/BODY_ROTATION/REVOCATION/RESTORE, and concurrency 1/4. The block design avoids a full factorial explosion and was not selected from observed outcomes.
