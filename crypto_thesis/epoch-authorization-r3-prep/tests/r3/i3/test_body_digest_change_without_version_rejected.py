import pytest

from epoch_auth_r3.header.digest import header_core_digest
from epoch_auth_r3.header.exceptions import HeaderErrorCode, HeaderValidationError
from epoch_auth_r3.header.version_chain import classify_update
from conftest import body_reference, build_header, make_context


def test_body_digest_change_without_body_version_is_rejected():
    one = build_header(make_context())
    two = build_header(
        make_context(2, header_core_digest(one.core).hex()),
        body_ref=body_reference(b"different-encrypted-body"),
    )
    with pytest.raises(HeaderValidationError) as exc:
        classify_update(one, two)
    assert exc.value.code == HeaderErrorCode.BODY_DIGEST_TRANSITION_INVALID
