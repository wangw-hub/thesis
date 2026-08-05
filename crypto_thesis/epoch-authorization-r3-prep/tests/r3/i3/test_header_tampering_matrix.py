from dataclasses import replace
import pytest
from epoch_auth_r3.header.exceptions import HeaderValidationError
from epoch_auth_r3.header.validator import VersionedHeaderValidatorV1
from conftest import verification


@pytest.mark.parametrize("field,value", [
    ("chain_id", 9), ("authorization_contract", "0x"+"99"*20),
    ("header_registry", "0x"+"98"*20), ("resource_id", "97"*32),
    ("body_digest", "96"*32), ("policy_digest", "95"*32),
    ("epoch", 9), ("state_version", 9), ("header_version", 9), ("key_version", 9),
])
def test_security_field_tampering_rejected(signed_header, field, value):
    with pytest.raises(HeaderValidationError):
        bad = replace(signed_header, core=replace(signed_header.core, **{field: value}))
        VersionedHeaderValidatorV1().validate(bad, verification(signed_header))


def test_envelope_ciphertext_tampering_rejected(signed_header):
    envelopes = list(signed_header.core.recipient_envelopes)
    ciphertext = envelopes[0].ciphertext
    envelopes[0] = replace(envelopes[0], ciphertext=bytes([ciphertext[0] ^ 1]) + ciphertext[1:])
    bad = replace(signed_header, core=replace(signed_header.core, recipient_envelopes=tuple(envelopes)))
    with pytest.raises(HeaderValidationError):
        VersionedHeaderValidatorV1().validate(bad, verification(signed_header))


def test_envelope_deletion_is_rejected_by_signature(signed_header):
    bad_core = replace(
        signed_header.core,
        recipient_envelopes=signed_header.core.recipient_envelopes[:1],
    )
    bad = replace(signed_header, core=bad_core)
    with pytest.raises(HeaderValidationError):
        VersionedHeaderValidatorV1().validate(bad, verification(signed_header))


def test_envelope_append_duplicate_is_rejected(signed_header):
    envelopes = signed_header.core.recipient_envelopes
    with pytest.raises(HeaderValidationError):
        replace(signed_header.core, recipient_envelopes=envelopes + (envelopes[0],))


def test_envelope_reordering_is_rejected(signed_header):
    with pytest.raises(HeaderValidationError):
        replace(
            signed_header.core,
            recipient_envelopes=tuple(reversed(signed_header.core.recipient_envelopes)),
        )
