from epoch_auth_r3.header.schema_v1 import RECIPIENT_MODE, SCHEMA_VERSION, SUITE_ID


def test_frozen_schema_and_suite(signed_header):
    core = signed_header.core
    assert core.schema_version == SCHEMA_VERSION == 1
    assert core.suite_id == SUITE_ID and core.recipient_mode == RECIPIENT_MODE
    assert core.body_digest == core.body_reference.digest_hex
