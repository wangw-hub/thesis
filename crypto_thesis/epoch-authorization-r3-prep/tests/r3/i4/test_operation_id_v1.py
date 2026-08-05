from dataclasses import replace
from epoch_auth_r3.database.operation_id import operation_id_v1
from conftest import event


def test_operation_id_is_deterministic_and_32_bytes():
    e = event()
    assert operation_id_v1(e) == operation_id_v1(e)
    assert len(operation_id_v1(e)) == 32


def test_every_bound_field_changes_operation_id():
    e = event()
    base = operation_id_v1(e)
    changes = [
        ("chain_id",2),("authorization_contract",b"a"*20),("header_registry",b"b"*20),
        ("event_signature",b"c"*32),("tx_hash",b"d"*32),("log_index",9),
        ("resource_id",b"e"*32),("new_epoch",9),("new_state_version",9),
        ("new_key_version",9),
    ]
    assert all(operation_id_v1(replace(e, **{k:v})) != base for k,v in changes)


def test_block_hash_and_header_version_are_evidence_not_operation_identity():
    e = event()
    assert operation_id_v1(replace(e, block_hash=b"z"*32, new_header_version=2)) == operation_id_v1(e)
