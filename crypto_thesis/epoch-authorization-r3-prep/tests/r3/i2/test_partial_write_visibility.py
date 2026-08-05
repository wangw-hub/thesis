from concurrent.futures import ThreadPoolExecutor
import threading

from epoch_auth_r3.storage import LocalObjectStore, ObjectKind


def test_readers_never_observe_partial_object(tmp_path):
    entered = threading.Event()
    release = threading.Event()

    def hook(point, temporary, final):
        if point == "F5":
            entered.set()
            assert release.wait(3)

    store = LocalObjectStore(tmp_path, _fault_hook=hook)
    with ThreadPoolExecutor(max_workers=2) as pool:
        future = pool.submit(store.put, b"complete-only", namespace="atomic", object_kind=ObjectKind.GENERIC_TEST)
        assert entered.wait(3)
        assert not list((tmp_path / "objects").rglob("*.obj"))
        release.set()
        ref = future.result(timeout=3)
    assert store.get(ref) == b"complete-only"
