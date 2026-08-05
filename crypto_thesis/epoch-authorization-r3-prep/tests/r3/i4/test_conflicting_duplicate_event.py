import pytest
from psycopg.errors import UniqueViolation
from epoch_auth_r3.database.job_repository import JobRepository
from conftest import event


def test_same_resource_target_different_operation_is_rejected_by_unique_design(db):
    repo=JobRepository(db)
    repo.insert_event(event(1))
    with pytest.raises(UniqueViolation):
        with db.transaction():
            db.execute("""INSERT INTO r3_control.header_update_job
              (job_id,operation_id,chain_id,authorization_contract,header_registry,event_signature,
               event_tx_hash,event_log_index,event_block_number,event_block_hash,resource_id,
               target_epoch,target_state_version,target_header_version,target_key_version)
              SELECT gen_random_uuid(),%s,chain_id,authorization_contract,header_registry,event_signature,
               event_tx_hash,event_log_index,event_block_number,event_block_hash,resource_id,
               target_epoch,target_state_version,target_header_version,target_key_version
              FROM r3_control.header_update_job LIMIT 1""",(b"x"*32,))
