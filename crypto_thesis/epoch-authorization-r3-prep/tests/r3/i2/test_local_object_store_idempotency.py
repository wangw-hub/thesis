from epoch_auth_r3.storage import ObjectKind


def test_repeated_put_is_idempotent(store):
    args = dict(namespace="same", object_kind=ObjectKind.GENERIC_TEST)
    first = store.put(b"same", **args)
    second = store.put(b"same", **args)
    assert first == second
    assert len(list((store.root / "objects").rglob("*.obj"))) == 1
