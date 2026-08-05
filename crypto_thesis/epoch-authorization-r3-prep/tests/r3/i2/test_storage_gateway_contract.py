from epoch_auth_r3.storage import ObjectKind, StorageGateway


def test_gateway_contract(store):
    assert isinstance(store, StorageGateway)
    ref = store.put(b"contract", namespace="test", object_kind=ObjectKind.GENERIC_TEST)
    assert store.exists(ref)
    assert store.verify(ref).verified
    assert store.get(ref) == b"contract"
