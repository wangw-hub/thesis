from concurrent.futures import ThreadPoolExecutor
from epoch_auth_r3.storage import ObjectKind


def test_concurrent_same_content_returns_one_reference(store):
    with ThreadPoolExecutor(max_workers=8) as pool:
        refs = list(pool.map(lambda _: store.put(b"same-concurrent", namespace="c", object_kind=ObjectKind.GENERIC_TEST), range(24)))
    assert len(set(refs)) == 1
    assert store.get(refs[0]) == b"same-concurrent"


def test_concurrent_different_content_never_overwrites(store):
    values = [f"object-{i}".encode() for i in range(16)]
    with ThreadPoolExecutor(max_workers=8) as pool:
        refs = list(pool.map(lambda d: store.put(d, namespace="c", object_kind=ObjectKind.GENERIC_TEST), values))
    assert len(set(refs)) == len(values)
    assert [store.get(r) for r in refs] == values
