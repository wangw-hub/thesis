import os
from epoch_auth_r3.storage import LocalObjectStore


def test_cleanup_only_old_owned_regular_temp_files(tmp_path):
    store = LocalObjectStore(tmp_path)
    old = store.root / "tmp" / ("r3tmp-" + "a"*32 + ".part")
    recent = store.root / "tmp" / ("r3tmp-" + "b"*32 + ".part")
    unrelated = store.root / "tmp" / "keep.txt"
    for p in (old, recent, unrelated): p.write_bytes(b"x")
    os.utime(old, (1, 1))
    removed = store.cleanup_temporary_files(older_than_seconds=10, now=100)
    assert removed == 1 and not old.exists() and recent.exists() and unrelated.exists()
    assert (store.root / "objects").is_dir()


def test_cleanup_skips_active_writer_name(tmp_path):
    store = LocalObjectStore(tmp_path)
    active = store.root / "tmp" / ("r3tmp-" + "c"*32 + ".part")
    active.write_bytes(b"x")
    os.utime(active, (1, 1))
    store._mark_temporary_active(active)
    try:
        assert store.cleanup_temporary_files(older_than_seconds=10, now=100) == 0
        assert active.exists()
    finally:
        store._mark_temporary_finished(active)
