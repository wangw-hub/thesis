import pytest
from epoch_auth_r3.header.digest import header_core_digest
from epoch_auth_r3.header.exceptions import HeaderValidationError
from epoch_auth_r3.header.validator import VersionedHeaderValidatorV1
from conftest import build_header, make_context, verification


def test_old_header_rejected_under_expected_new_version_context():
    old = build_header(make_context(1, None))
    new = build_header(make_context(2, header_core_digest(old.core).hex()))
    with pytest.raises(HeaderValidationError):
        VersionedHeaderValidatorV1().validate(old, verification(new))
