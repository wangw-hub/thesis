import pytest
from epoch_auth_r3.header.exceptions import HeaderErrorCode, HeaderValidationError
from conftest import build_header, recipients


def test_duplicate_recipient_key_id_rejected():
    values = recipients()
    values.append(values[0])
    with pytest.raises(HeaderValidationError) as exc:
        build_header(recipient_list=values)
    assert exc.value.code == HeaderErrorCode.RECIPIENT_DUPLICATE
