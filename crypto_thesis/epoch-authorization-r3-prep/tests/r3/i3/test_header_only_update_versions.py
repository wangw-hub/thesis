from epoch_auth_r3.header.digest import header_core_digest
from epoch_auth_r3.header.version_chain import HeaderUpdateKind, classify_update
from conftest import build_header, make_context


def test_header_only_keeps_body_and_key_versions():
    one = build_header(make_context())
    two = build_header(make_context(2, header_core_digest(one.core).hex()))
    assert classify_update(one, two) == HeaderUpdateKind.HEADER_ONLY
    assert two.core.body_digest == one.core.body_digest
    assert two.core.body_version == two.core.key_version == 1
