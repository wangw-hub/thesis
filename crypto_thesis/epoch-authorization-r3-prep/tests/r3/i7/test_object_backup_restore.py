import hashlib

from epoch_auth_r3.recovery.backup_restore import ObjectBackupRestore
from epoch_auth_r3.recovery.models import RecoveryDisposition
from epoch_auth_r3.storage import LocalObjectStore, ObjectKind, ObjectReferenceV1


def _reference(data, kind=ObjectKind.HEADER):
    return ObjectReferenceV1(
        1, "local", "recovery", kind, "sha256",
        hashlib.sha256(data).hexdigest(), len(data),
    )


def test_verified_backup_restores_exact_object(tmp_path):
    data = b"non-sensitive-i7-header"
    backup_root = tmp_path / "backup"
    backup_root.mkdir()
    backup = backup_root / "object.bin"
    backup.write_bytes(data)
    store = LocalObjectStore(tmp_path / "store")
    result = ObjectBackupRestore(store, backup_root).restore(_reference(data), backup)
    assert result.restored and store.get(_reference(data)) == data


def test_missing_backup_is_irrecoverable(tmp_path):
    result = ObjectBackupRestore(
        LocalObjectStore(tmp_path / "store"), tmp_path / "backup"
    ).restore(_reference(b"x"), None)
    assert result.disposition == RecoveryDisposition.IRRECOVERABLE_CONTENT_LOSS


def test_corrupt_backup_fails_closed(tmp_path):
    root = tmp_path / "backup"
    root.mkdir()
    path = root / "bad"
    path.write_bytes(b"bad")
    result = ObjectBackupRestore(LocalObjectStore(tmp_path / "store"), root).restore(
        _reference(b"good"), path
    )
    assert result.disposition == RecoveryDisposition.FAIL_CLOSED_CORRUPT_OBJECT


def test_backup_outside_trust_root_rejected(tmp_path):
    root = tmp_path / "backup"
    root.mkdir()
    outside = tmp_path / "outside"
    outside.write_bytes(b"x")
    result = ObjectBackupRestore(LocalObjectStore(tmp_path / "store"), root).restore(
        _reference(b"x"), outside
    )
    assert result.disposition == RecoveryDisposition.CONFLICT


def test_body_verified_backup_restores_exact_object(tmp_path):
    data = b"non-sensitive-i7-body"
    root = tmp_path / "backup"
    root.mkdir()
    path = root / "body.bin"
    path.write_bytes(data)
    store = LocalObjectStore(tmp_path / "store")
    reference = _reference(data, ObjectKind.BODY)
    result = ObjectBackupRestore(store, root).restore(reference, path)
    assert result.restored and store.get(reference) == data


def test_body_without_backup_is_irrecoverable(tmp_path):
    reference = _reference(b"body", ObjectKind.BODY)
    result = ObjectBackupRestore(
        LocalObjectStore(tmp_path / "store"), tmp_path / "backup"
    ).restore(reference, None)
    assert result.disposition == RecoveryDisposition.IRRECOVERABLE_CONTENT_LOSS
