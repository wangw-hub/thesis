from dataclasses import replace
import pytest
from epoch_auth_r3.header.exceptions import HeaderValidationError
from epoch_auth_r3.header.recipient import RecipientHeaderOpenerV1
from conftest import private_key, verification


@pytest.mark.parametrize("field,value", [
    ("expected_resource_id", "55"*32), ("expected_epoch", 99),
    ("expected_header_version", 9), ("expected_chain_id", 9),
])
def test_external_context_substitution_rejected(signed_header, field, value):
    ctx = replace(verification(signed_header), **{field: value})
    with pytest.raises(HeaderValidationError):
        RecipientHeaderOpenerV1().open_content_key(
            header=signed_header, recipient_key_id="aa"*32, user_version=1,
            recipient_private_key=private_key(7), verification_context=ctx,
        )
