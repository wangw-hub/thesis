import pytest
from dataclasses import replace
from epoch_auth_r3.header.digest import header_core_digest
from epoch_auth_r3.header.exceptions import HeaderValidationError
from epoch_auth_r3.header.models import SignedVersionedHeaderV1
from epoch_auth_r3.header.recipient import RecipientHeaderOpenerV1
from epoch_auth_r3.header.signature import sign_core
from epoch_auth_r3.header.version_chain import validate_version_chain
from conftest import TEST_ONLY_HEADER_SEED, build_header, make_context, private_key, verification


def chain():
    one = build_header(make_context(1, None))
    two = build_header(make_context(2, header_core_digest(one.core).hex()))
    three = build_header(make_context(3, header_core_digest(two.core).hex()))
    return one, two, three


def test_v1_v2_v3_chain_and_skip_rejected():
    one, two, three = chain()
    validate_version_chain([one, two, three])
    with pytest.raises(HeaderValidationError): validate_version_chain([one, three])


def test_v2_envelope_cannot_be_copied_to_v3_even_after_resigning():
    one, two, three = chain()
    copied_core = replace(three.core, recipient_envelopes=two.core.recipient_envelopes)
    copied = SignedVersionedHeaderV1(
        copied_core, sign_core(copied_core, TEST_ONLY_HEADER_SEED, "test-header-key-v1")
    )
    with pytest.raises(HeaderValidationError):
        RecipientHeaderOpenerV1().open_content_key(
            header=copied, recipient_key_id="aa"*32, user_version=1,
            recipient_private_key=private_key(7), verification_context=verification(copied),
        )
