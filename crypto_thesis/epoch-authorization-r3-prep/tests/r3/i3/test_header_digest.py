from dataclasses import replace
from epoch_auth_r3.header.digest import header_core_digest, header_object_digest


def test_core_digest_changes_for_security_field_and_differs_from_object_digest(signed_header):
    original = header_core_digest(signed_header.core)
    changed = replace(signed_header.core, epoch=signed_header.core.epoch + 1)
    assert header_core_digest(changed) != original
    assert header_object_digest(signed_header.to_canonical_bytes()) != original.hex()
