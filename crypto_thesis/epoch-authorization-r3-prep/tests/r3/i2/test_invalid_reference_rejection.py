from dataclasses import replace
import pytest
from epoch_auth_r3.storage import ObjectKind
from epoch_auth_r3.storage.exceptions import InvalidReferenceError


def test_non_reference_rejected(store):
    with pytest.raises(InvalidReferenceError): store.get({"digest": "bad"})
    assert not store.verify({"digest": "bad"}).reference_valid


def test_backend_digest_and_uppercase_are_constructor_rejected():
    from epoch_auth_r3.storage.references import ObjectReferenceV1
    for kwargs in [
        dict(backend="ipfs", digest_algorithm="sha256", digest_hex="aa"*32),
        dict(backend="local", digest_algorithm="sha512", digest_hex="aa"*32),
        dict(backend="local", digest_algorithm="sha256", digest_hex="AA"*32),
    ]:
        with pytest.raises(InvalidReferenceError):
            ObjectReferenceV1(1, kwargs["backend"], "x", ObjectKind.BODY, kwargs["digest_algorithm"], kwargs["digest_hex"], 1)
