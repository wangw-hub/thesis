import pytest
from epoch_auth_r3.header.exceptions import HeaderValidationError
from epoch_auth_r3.header.models import SignedVersionedHeaderV1


def test_unknown_missing_duplicate_and_truncated_json_rejected(signed_header):
    text = signed_header.to_canonical_bytes().decode()
    variants = [
        text.replace('"core":{', '"unknown":1,"core":{', 1),
        text.replace('"signature":{', '"removedSignature":{', 1),
        text.replace('"core":{', '"core":{},"core":{', 1),
        text[:-1],
        text + "{}",
    ]
    for value in variants:
        with pytest.raises(HeaderValidationError):
            SignedVersionedHeaderV1.from_strict_json_bytes(value)
