import pytest
from epoch_auth_r3.header.exceptions import HeaderValidationError
from epoch_auth_r3.header.recipient import RecipientHeaderOpenerV1
from conftest import private_key, verification


def test_envelope_cannot_be_opened_by_other_recipient(signed_header):
    with pytest.raises(HeaderValidationError):
        RecipientHeaderOpenerV1().open_content_key(
            header=signed_header, recipient_key_id="aa"*32, user_version=1,
            recipient_private_key=private_key(9), verification_context=verification(signed_header),
        )
