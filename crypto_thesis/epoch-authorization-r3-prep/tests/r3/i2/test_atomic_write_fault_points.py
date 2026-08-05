import pytest
from epoch_auth_r3.storage import LocalObjectStore, ObjectKind
from epoch_auth_r3.storage.exceptions import InjectedStorageFault
from epoch_auth_r3.storage.testing import FaultInjector


@pytest.mark.parametrize("point", [f"F{i}" for i in range(1, 8)])
def test_fault_points_never_publish_partial_success(tmp_path, point):
    root = tmp_path / point
    injector = FaultInjector(point)
    store = LocalObjectStore(root, _fault_hook=injector)
    with pytest.raises(InjectedStorageFault):
        store.put(b"fault-object", namespace="fault", object_kind=ObjectKind.GENERIC_TEST)
    objects = list((root / "objects").rglob("*.obj"))
    assert all(p.read_bytes() == b"fault-object" for p in objects)
    assert not list((root / "tmp").glob("r3tmp-*.part"))
    clean = LocalObjectStore(root)
    ref = clean.put(b"fault-object", namespace="fault", object_kind=ObjectKind.GENERIC_TEST)
    assert clean.get(ref) == b"fault-object"


def test_existing_object_fault_f8_is_not_reported_success(tmp_path):
    clean = LocalObjectStore(tmp_path)
    clean.put(b"x", namespace="fault", object_kind=ObjectKind.GENERIC_TEST)
    failing = LocalObjectStore(tmp_path, _fault_hook=FaultInjector("F8"))
    with pytest.raises(InjectedStorageFault):
        failing.put(b"x", namespace="fault", object_kind=ObjectKind.GENERIC_TEST)
