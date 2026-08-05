from epoch_auth_r3.header.digest import header_core_digest
from epoch_auth_r3.header.version_chain import HeaderUpdateKind, classify_update
from conftest import body_reference, build_header, make_context


def test_body_rotation_increments_body_and_key_together():
    one = build_header(make_context())
    two = build_header(
        make_context(2, header_core_digest(one.core).hex(), body_version=2, key_version=2),
        body_ref=body_reference(b"rotated-encrypted-body"),
    )
    assert classify_update(one, two) == HeaderUpdateKind.BODY_ROTATION
