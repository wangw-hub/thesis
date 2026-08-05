import pytest

from epoch_auth_r3.header.exceptions import HeaderValidationError
from conftest import build_header, make_context


def test_body_increment_without_key_increment_is_rejected():
    with pytest.raises(HeaderValidationError):
        build_header(make_context(body_version=2, key_version=1))
