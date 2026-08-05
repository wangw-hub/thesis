import json
import pytest

from epoch_auth_r3.storage.exceptions import InvalidReferenceError
from epoch_auth_r3.storage.references import ObjectKind, ObjectReferenceV1


def valid():
    return ObjectReferenceV1(1, "local", "thesis-test", ObjectKind.BODY, "sha256", "ab" * 32, 7)


def test_canonical_reference_roundtrip_and_identity():
    ref = valid()
    assert ObjectReferenceV1.from_strict_dict(ref.to_canonical_dict()) == ref
    assert ObjectReferenceV1.from_strict_json(ref.to_canonical_bytes()) == ref
    assert json.loads(ref.to_canonical_bytes()) == ref.to_canonical_dict()
    assert ref.digest_identity() == "sha256:" + "ab" * 32


@pytest.mark.parametrize("change", [
    {"schema_version": 2}, {"backend": "ipfs"}, {"namespace": "../x"},
    {"digest_algorithm": "md5"}, {"digest_hex": "AB" * 32}, {"size_bytes": 1.5},
])
def test_invalid_reference_fields_rejected(change):
    values = vars(valid()) | change
    with pytest.raises(InvalidReferenceError): ObjectReferenceV1(**values)


def test_unknown_missing_and_object_kind_rejected():
    value = valid().to_canonical_dict()
    for changed in ({**value, "extra": 1}, {k:v for k,v in value.items() if k != "backend"}, {**value, "objectKind": "OTHER"}):
        with pytest.raises(InvalidReferenceError): ObjectReferenceV1.from_strict_dict(changed)
    duplicate = valid().to_canonical_bytes().decode().replace(
        '"backend":"local"', '"backend":"local","backend":"local"'
    )
    with pytest.raises(InvalidReferenceError): ObjectReferenceV1.from_strict_json(duplicate)
