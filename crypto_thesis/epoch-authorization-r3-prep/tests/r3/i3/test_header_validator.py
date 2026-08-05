import pytest
from epoch_auth_r3.header.exceptions import HeaderErrorCode, HeaderValidationError
from epoch_auth_r3.header.validator import VersionedHeaderValidatorV1
from conftest import verification


def test_trusted_context_required(signed_header):
    assert VersionedHeaderValidatorV1().validate(signed_header, verification(signed_header)).verified
    with pytest.raises(HeaderValidationError) as exc:
        VersionedHeaderValidatorV1().validate(
            signed_header, verification(signed_header, trusted_issuer_key_id="other")
        )
    assert exc.value.code == HeaderErrorCode.ISSUER_KEY_ID_MISMATCH


def test_wrong_trusted_issuer_public_key_is_rejected(signed_header):
    with pytest.raises(HeaderValidationError) as exc:
        VersionedHeaderValidatorV1().validate(
            signed_header,
            verification(signed_header, trusted_issuer_public_key=b"\x01" * 32),
        )
    assert exc.value.code == HeaderErrorCode.HEADER_SIGNATURE_INVALID
