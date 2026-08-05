import os
import stat
import pytest
from epoch_auth_r3.storage import ObjectKind
from epoch_auth_r3.storage.exceptions import PathSecurityError


def test_object_symlink_rejected(store, tmp_path, monkeypatch):
    ref = store.put(b"target", namespace="link", object_kind=ObjectKind.GENERIC_TEST)
    path = next((store.root / "objects").rglob("*.obj"))
    external = tmp_path / "external"
    external.write_bytes(b"target")
    path.unlink()
    try:
        path.symlink_to(external)
    except OSError:
        original = os.lstat
        monkeypatch.setattr(
            "epoch_auth_r3.storage.local_store.os.lstat",
            lambda candidate: type("S", (), {"st_mode": stat.S_IFLNK})()
            if candidate == path else original(candidate),
        )
        original_exists = type(path).exists
        monkeypatch.setattr(
            type(path), "exists",
            lambda candidate: True if candidate == path else original_exists(candidate),
        )
    assert store.verify(ref).symlink_rejected
    with pytest.raises(PathSecurityError): store.get(ref)
