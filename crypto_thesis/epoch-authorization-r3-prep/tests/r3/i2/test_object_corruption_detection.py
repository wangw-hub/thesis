from dataclasses import replace
import pytest
from epoch_auth_r3.storage import ObjectKind
from epoch_auth_r3.storage.exceptions import CorruptObjectError


@pytest.mark.parametrize("mutation", ["truncate", "append", "replace"])
def test_corrupt_objects_fail_verify_and_get(store, mutation):
    ref = store.put(b"original", namespace="bad", object_kind=ObjectKind.GENERIC_TEST)
    path = next((store.root / "objects").rglob("*.obj"))
    path.write_bytes({"truncate": b"orig", "append": b"original+", "replace": b"replaced"}[mutation])
    assert not store.verify(ref).verified
    with pytest.raises(CorruptObjectError): store.get(ref)
    with pytest.raises(CorruptObjectError):
        store.put(b"original", namespace="bad", object_kind=ObjectKind.GENERIC_TEST)


def test_forged_size_reference_rejected(store):
    ref = store.put(b"size", namespace="bad", object_kind=ObjectKind.GENERIC_TEST)
    forged = replace(ref, size_bytes=999)
    assert not store.verify(forged).verified
    with pytest.raises(CorruptObjectError): store.get(forged)
