import pytest
from epoch_auth_r3.storage import ObjectKind
from epoch_auth_r3.storage.exceptions import InvalidReferenceError


@pytest.mark.parametrize("namespace", ["", ".", "..", "../x", "..\\x", "/abs", "C:drive", "\\\\server", "a/b", "a\\b", "http:x", "a\x00b", "a\nb"])
def test_namespace_path_injection_rejected(store, namespace):
    with pytest.raises(InvalidReferenceError):
        store.put(b"x", namespace=namespace, object_kind=ObjectKind.GENERIC_TEST)
