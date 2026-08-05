import hashlib
import pytest
from epoch_auth_r3.storage import ObjectKind
from epoch_auth_r3.storage.exceptions import DigestMismatchError


def test_put_get_content_address_and_expected_digest(store):
    data = b"immutable test object"
    digest = hashlib.sha256(data).hexdigest()
    ref = store.put(data, namespace="body", object_kind=ObjectKind.BODY, expected_digest=digest)
    assert ref.digest_hex == digest and ref.size_bytes == len(data)
    assert store.get(ref) == data and store.verify(ref).verified


def test_wrong_expected_digest_rejected_without_object(store):
    with pytest.raises(DigestMismatchError):
        store.put(b"x", namespace="body", object_kind=ObjectKind.BODY, expected_digest="00"*32)
    assert not list((store.root / "objects").rglob("*.obj"))
