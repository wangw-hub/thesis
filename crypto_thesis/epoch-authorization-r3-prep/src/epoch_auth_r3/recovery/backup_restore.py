from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

from epoch_auth_r3.storage import LocalObjectStore, ObjectReferenceV1

from .models import RecoveryDisposition


@dataclass(frozen=True)
class RestoreResult:
    disposition: RecoveryDisposition
    restored: bool


class ObjectBackupRestore:
    def __init__(self, store: LocalObjectStore, backup_root: Path):
        self.store = store
        self.backup_root = backup_root.resolve()

    def restore(self, reference: ObjectReferenceV1, backup: Path | None) -> RestoreResult:
        if backup is None or not backup.exists():
            return RestoreResult(RecoveryDisposition.IRRECOVERABLE_CONTENT_LOSS, False)
        path = backup.resolve()
        if self.backup_root not in path.parents or path.is_symlink() or not path.is_file():
            return RestoreResult(RecoveryDisposition.CONFLICT, False)
        data = path.read_bytes()
        if hashlib.sha256(data).hexdigest() != reference.digest_hex:
            return RestoreResult(RecoveryDisposition.FAIL_CLOSED_CORRUPT_OBJECT, False)
        restored = self.store.put(
            data,
            namespace=reference.namespace,
            object_kind=reference.object_kind,
            expected_digest=reference.digest_hex,
        )
        if restored != reference or not self.store.verify(reference).verified:
            return RestoreResult(RecoveryDisposition.CONFLICT, False)
        return RestoreResult(RecoveryDisposition.AUTO_RECOVERABLE, True)
