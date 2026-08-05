import pytest
from psycopg.errors import CheckViolation


def test_byte_length_constraint_is_database_enforced(db):
    with pytest.raises(CheckViolation):
        with db.transaction():
            db.execute("""INSERT INTO r3_control.revocation_event_cursor
                (source_id,chain_id,authorization_contract,next_block_number,next_log_index)
                VALUES ('bad',1,%s,0,0)""",(b"x",))
