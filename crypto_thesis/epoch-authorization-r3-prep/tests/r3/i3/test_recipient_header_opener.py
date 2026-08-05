import pytest
from epoch_auth_r3.header.exceptions import HeaderErrorCode, HeaderValidationError
from epoch_auth_r3.header.recipient import RecipientHeaderOpenerV1
from conftest import TEST_ONLY_CK, private_key, verification


def test_authorized_recipient_opens_and_nonrecipient_wrong_version_fail(signed_header):
    opener = RecipientHeaderOpenerV1()
    args = dict(header=signed_header, recipient_private_key=private_key(7), verification_context=verification(signed_header))
    assert opener.open_content_key(recipient_key_id="aa"*32, user_version=1, **args) == TEST_ONLY_CK
    for key_id, version in (("cc"*32, 1), ("aa"*32, 2)):
        with pytest.raises(HeaderValidationError):
            opener.open_content_key(recipient_key_id=key_id, user_version=version, **args)
