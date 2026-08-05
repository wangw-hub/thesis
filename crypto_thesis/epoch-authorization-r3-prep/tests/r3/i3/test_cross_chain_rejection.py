import pytest
from epoch_auth_r3.header.exceptions import HeaderValidationError
from epoch_auth_r3.header.validator import VersionedHeaderValidatorV1
from conftest import verification


def test_cross_chain_context_rejected(signed_header):
    with pytest.raises(HeaderValidationError):
        VersionedHeaderValidatorV1().validate(signed_header, verification(signed_header, expected_chain_id=99))
