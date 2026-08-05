import pytest
from epoch_auth_r3.storage import ObjectKind
from epoch_auth_r3.storage.exceptions import CorruptObjectError


def test_stored_body_tamper_and_cross_reference_replacement_rejected(store):
    first = store.put(b"body-one", namespace="body", object_kind=ObjectKind.BODY)
    second = store.put(b"body-two", namespace="body", object_kind=ObjectKind.BODY)
    first_path = [p for p in (store.root / "objects").rglob("*.obj") if p.name.startswith(first.digest_hex)][0]
    first_path.write_bytes(store.get(second))
    assert not store.verify(first).verified
    with pytest.raises(CorruptObjectError): store.get(first)
