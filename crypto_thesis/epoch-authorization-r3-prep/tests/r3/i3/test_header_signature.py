from dataclasses import replace
import pytest
from epoch_auth_r3.header.exceptions import HeaderValidationError
from epoch_auth_r3.header.validator import VersionedHeaderValidatorV1
from conftest import verification


def test_signature_verifies_and_tamper_fails(signed_header):
    validator = VersionedHeaderValidatorV1()
    assert validator.validate(signed_header, verification(signed_header)).verified
    bad = replace(signed_header, signature=replace(signed_header.signature, signature=b"x"+signed_header.signature.signature[1:]))
    with pytest.raises(HeaderValidationError): validator.validate(bad, verification(signed_header))


@pytest.mark.parametrize("signature", [b"x" * 63, b"x" * 65])
def test_truncated_or_extended_signature_is_rejected(signed_header, signature):
    with pytest.raises(HeaderValidationError):
        replace(signed_header.signature, signature=signature)
