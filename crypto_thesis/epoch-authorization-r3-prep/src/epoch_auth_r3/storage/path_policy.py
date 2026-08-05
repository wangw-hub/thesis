from __future__ import annotations

import os
import stat
from pathlib import Path

from .exceptions import PathSecurityError
from .references import ObjectReferenceV1, validate_namespace


def _inside(root: Path, candidate: Path) -> None:
    try:
        common = os.path.commonpath((os.path.abspath(root), os.path.abspath(candidate)))
    except ValueError as exc:
        raise PathSecurityError("PATH_ESCAPE") from exc
    if os.path.normcase(common) != os.path.normcase(os.path.abspath(root)):
        raise PathSecurityError("PATH_ESCAPE")


class StoragePathPolicy:
    def __init__(self, root: Path) -> None:
        self.root = root.resolve(strict=True)
        if self.root.is_symlink() or not self.root.is_dir():
            raise PathSecurityError("INVALID_STORAGE_ROOT")

    def ensure_safe_directory(self, directory: Path) -> None:
        _inside(self.root, directory)
        relative = directory.relative_to(self.root)
        current = self.root
        for part in relative.parts:
            current = current / part
            current.mkdir(exist_ok=True)
            mode = os.lstat(current).st_mode
            if stat.S_ISLNK(mode) or not stat.S_ISDIR(mode):
                raise PathSecurityError("SYMLINK_OR_NON_DIRECTORY_COMPONENT")

    def object_path(self, reference: ObjectReferenceV1) -> Path:
        namespace = validate_namespace(reference.namespace)
        path = (
            self.root
            / "objects"
            / namespace
            / "sha256"
            / reference.digest_hex[:2]
            / reference.digest_hex[2:4]
            / f"{reference.digest_hex}.obj"
        )
        _inside(self.root, path)
        return path

    def tmp_directory(self) -> Path:
        path = self.root / "tmp"
        _inside(self.root, path)
        return path
