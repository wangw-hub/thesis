import pytest
from epoch_auth_r3.header.exceptions import HeaderValidationError
from epoch_auth_r3.header.validator import VersionedHeaderValidatorV1
from conftest import verification


@pytest.mark.parametrize("field", ["expected_authorization_contract", "expected_header_registry"])
def test_cross_contract_context_rejected(signed_header, field):
    with pytest.raises(HeaderValidationError):
        VersionedHeaderValidatorV1().validate(signed_header, verification(signed_header, **{field: "0x"+"99"*20}))
