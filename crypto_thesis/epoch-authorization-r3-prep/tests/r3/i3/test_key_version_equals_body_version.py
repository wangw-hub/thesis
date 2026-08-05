import pytest

from epoch_auth_r3.header.exceptions import HeaderErrorCode, HeaderValidationError
from conftest import build_header, make_context


def test_key_version_must_equal_body_version():
    with pytest.raises(HeaderValidationError) as exc:
        build_header(make_context(body_version=1, key_version=2))
    assert exc.value.code == HeaderErrorCode.KEY_BODY_VERSION_MISMATCH
