from dataclasses import replace
import pytest
from epoch_auth_r3.header.exceptions import HeaderErrorCode, HeaderValidationError
from epoch_auth_r3.header.validator import VersionedHeaderValidatorV1
from conftest import verification


def test_context_mismatch_precedes_signature_acceptance(signed_header):
    bad = replace(signed_header, core=replace(signed_header.core, epoch=99))
    with pytest.raises(HeaderValidationError) as exc:
        VersionedHeaderValidatorV1().validate(bad, verification(signed_header))
    assert exc.value.code == HeaderErrorCode.EPOCH_MISMATCH
