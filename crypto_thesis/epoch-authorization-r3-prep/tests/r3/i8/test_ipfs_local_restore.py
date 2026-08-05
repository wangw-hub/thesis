def _object_path(store, reference):
    return store._paths.object_path(reference)


def test_local_header_missing_restored(i8_fixture):
    ref = i8_fixture["header_ref"]
    replica = i8_fixture["gateway"].replicate(ref)
    _object_path(i8_fixture["store"], ref).unlink()
    assert i8_fixture["gateway"].restore_local(ref, replica) == ref
    assert i8_fixture["store"].get(ref) == i8_fixture["header_bytes"]


def test_local_body_missing_restored(i8_fixture):
    ref = i8_fixture["body_ref"]
    replica = i8_fixture["gateway"].replicate(ref)
    _object_path(i8_fixture["store"], ref).unlink()
    i8_fixture["gateway"].restore_local(ref, replica)
    assert i8_fixture["store"].get(ref) == i8_fixture["body_bytes"]


def test_local_corrupt_object_quarantined_then_restored(i8_fixture):
    ref = i8_fixture["body_ref"]
    replica = i8_fixture["gateway"].replicate(ref)
    _object_path(i8_fixture["store"], ref).write_bytes(b"corrupt")
    i8_fixture["gateway"].restore_local(ref, replica)
    assert i8_fixture["store"].verify(ref).verified
    assert len(list((i8_fixture["store"].root / "quarantine").iterdir())) == 1


def test_existing_verified_object_is_idempotent(i8_fixture):
    ref = i8_fixture["header_ref"]
    replica = i8_fixture["gateway"].replicate(ref)
    assert i8_fixture["gateway"].restore_local(ref, replica) == ref
