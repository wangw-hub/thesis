from __future__ import annotations

import hashlib
import os
import stat
import time
import threading
import uuid
from pathlib import Path

from .atomic_write import FaultHook, atomic_publish, validate_existing_with_fault
from .exceptions import (
    CorruptObjectError,
    DigestMismatchError,
    InvalidReferenceError,
    PathSecurityError,
    StorageError,
)
from .path_policy import StoragePathPolicy
from .references import ObjectKind, ObjectReferenceV1, validate_digest, validate_namespace
from .verification import FailureCode, ObjectVerificationResult

_TMP_PREFIX = "r3tmp-"
_TMP_SUFFIX = ".part"


class LocalObjectStore:
    def __init__(self, root: str | os.PathLike[str], *, _fault_hook: FaultHook | None = None):
        root_path = Path(root)
        root_path.mkdir(parents=True, exist_ok=True)
        self._paths = StoragePathPolicy(root_path)
        self._paths.ensure_safe_directory(self._paths.tmp_directory())
        self._paths.ensure_safe_directory(self._paths.root / "objects")
        self._paths.ensure_safe_directory(self._paths.root / "quarantine")
        self._paths.ensure_safe_directory(self._paths.root / "audit")
        self._fault_hook = _fault_hook
        self._active_lock = threading.Lock()
        self._active_temporary: set[str] = set()

    @property
    def root(self) -> Path:
        return self._paths.root

    def put(
        self,
        data: bytes,
        *,
        namespace: str,
        object_kind: ObjectKind,
        expected_digest: str | None = None,
    ) -> ObjectReferenceV1:
        if not isinstance(data, bytes):
            raise TypeError("put accepts bytes only")
        validate_namespace(namespace)
        if not isinstance(object_kind, ObjectKind):
            raise InvalidReferenceError("INVALID_OBJECT_KIND")
        digest = hashlib.sha256(data).hexdigest()
        if expected_digest is not None:
            if validate_digest(expected_digest) != digest:
                raise DigestMismatchError("EXPECTED_DIGEST_MISMATCH")
        reference = ObjectReferenceV1(1, "local", namespace, object_kind, "sha256", digest, len(data))
        final_path = self._paths.object_path(reference)
        self._paths.ensure_safe_directory(final_path.parent)

        def verify_file(path: Path) -> None:
            self._verify_path(path, reference)

        if final_path.exists() or final_path.is_symlink():
            validate_existing_with_fault(final_path, verify_file, self._fault_hook)
            return reference
        atomic_publish(
            data,
            final_path=final_path,
            temporary_directory=self._paths.tmp_directory(),
            verify_file=verify_file,
            fault_hook=self._fault_hook,
            on_temporary_created=self._mark_temporary_active,
            on_temporary_finished=self._mark_temporary_finished,
        )
        return reference

    def _mark_temporary_active(self, path: Path) -> None:
        with self._active_lock:
            self._active_temporary.add(path.name)

    def _mark_temporary_finished(self, path: Path) -> None:
        with self._active_lock:
            self._active_temporary.discard(path.name)

    def _verify_path(self, path: Path, reference: ObjectReferenceV1) -> None:
        try:
            mode = os.lstat(path).st_mode
        except FileNotFoundError as exc:
            raise CorruptObjectError("OBJECT_NOT_FOUND") from exc
        if stat.S_ISLNK(mode):
            raise PathSecurityError("SYMLINK_REJECTED")
        if not stat.S_ISREG(mode):
            raise CorruptObjectError("NOT_REGULAR_FILE")
        data = path.read_bytes()
        if len(data) != reference.size_bytes:
            raise CorruptObjectError("SIZE_MISMATCH")
        if hashlib.sha256(data).hexdigest() != reference.digest_hex:
            raise CorruptObjectError("DIGEST_MISMATCH")

    def get(self, reference: ObjectReferenceV1) -> bytes:
        if not isinstance(reference, ObjectReferenceV1):
            raise InvalidReferenceError("INVALID_REFERENCE")
        path = self._paths.object_path(reference)
        self._verify_path(path, reference)
        data = path.read_bytes()
        if len(data) != reference.size_bytes or hashlib.sha256(data).hexdigest() != reference.digest_hex:
            raise CorruptObjectError("OBJECT_CHANGED_DURING_READ")
        return data

    def exists(self, reference: ObjectReferenceV1) -> bool:
        if not isinstance(reference, ObjectReferenceV1):
            raise InvalidReferenceError("INVALID_REFERENCE")
        path = self._paths.object_path(reference)
        return path.exists() or path.is_symlink()

    def verify(self, reference: ObjectReferenceV1) -> ObjectVerificationResult:
        if not isinstance(reference, ObjectReferenceV1):
            return ObjectVerificationResult(reference_valid=False, failure_code=FailureCode.INVALID_REFERENCE)
        try:
            path = self._paths.object_path(reference)
            if not path.exists() and not path.is_symlink():
                return ObjectVerificationResult(failure_code=FailureCode.OBJECT_NOT_FOUND)
            mode = os.lstat(path).st_mode
            if stat.S_ISLNK(mode):
                return ObjectVerificationResult(exists=True, symlink_rejected=True, failure_code=FailureCode.SYMLINK_REJECTED)
            if not stat.S_ISREG(mode):
                return ObjectVerificationResult(exists=True, failure_code=FailureCode.NOT_REGULAR_FILE)
            data = path.read_bytes()
            size_matches = len(data) == reference.size_bytes
            digest_matches = hashlib.sha256(data).hexdigest() == reference.digest_hex
            code = FailureCode.NONE if size_matches and digest_matches else (
                FailureCode.SIZE_MISMATCH if not size_matches else FailureCode.DIGEST_MISMATCH
            )
            return ObjectVerificationResult(
                exists=True, regular_file=True, size_matches=size_matches,
                digest_matches=digest_matches, verified=size_matches and digest_matches,
                failure_code=code,
            )
        except PathSecurityError:
            return ObjectVerificationResult(failure_code=FailureCode.PATH_ESCAPE)
        except OSError:
            return ObjectVerificationResult(failure_code=FailureCode.READ_ERROR)

    def cleanup_temporary_files(self, *, older_than_seconds: int, now: float | None = None) -> int:
        if type(older_than_seconds) is not int or older_than_seconds < 0:
            raise ValueError("invalid cleanup threshold")
        current_time = time.time() if now is None else now
        removed = 0
        temporary_directory = self._paths.tmp_directory()
        for candidate in temporary_directory.iterdir():
            if not candidate.name.startswith(_TMP_PREFIX) or not candidate.name.endswith(_TMP_SUFFIX):
                continue
            with self._active_lock:
                if candidate.name in self._active_temporary:
                    continue
            mode = os.lstat(candidate).st_mode
            if stat.S_ISLNK(mode) or not stat.S_ISREG(mode):
                continue
            if current_time - candidate.stat().st_mtime < older_than_seconds:
                continue
            candidate.unlink()
            removed += 1
        return removed

    def controlled_delete_for_recovery_test(
        self, reference: ObjectReferenceV1
    ) -> None:
        """Delete one verified object only for an explicitly controlled restore test."""
        if not self.verify(reference).verified:
            raise StorageError("CONTROLLED_DELETE_REQUIRES_VERIFIED_OBJECT")
        path = self._paths.object_path(reference)
        path.unlink()
        if path.exists() or path.is_symlink():
            raise StorageError("CONTROLLED_DELETE_FAILED")

    def quarantine_corrupt(self, reference: ObjectReferenceV1) -> Path:
        """Move a verified-corrupt object aside; never overwrite it in place."""
        result = self.verify(reference)
        if not result.exists or result.verified:
            raise StorageError("OBJECT_NOT_CORRUPT")
        source = self._paths.object_path(reference)
        target = self._paths.root / "quarantine" / (
            f"{reference.digest_hex}-{uuid.uuid4().hex}.corrupt"
        )
        source.replace(target)
        return target
