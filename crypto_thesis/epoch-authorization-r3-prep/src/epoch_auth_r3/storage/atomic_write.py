from __future__ import annotations

import os
import uuid
from pathlib import Path
from typing import Callable

from .exceptions import StorageError

FaultHook = Callable[[str, Path, Path], None]
FAULT_POINTS = tuple(f"F{i}" for i in range(1, 9))


def _fault(hook: FaultHook | None, point: str, temporary: Path, final: Path) -> None:
    if hook is not None:
        hook(point, temporary, final)


def fsync_directory(directory: Path) -> bool:
    if os.name == "nt":
        return False
    descriptor = os.open(directory, os.O_RDONLY)
    try:
        os.fsync(descriptor)
        return True
    finally:
        os.close(descriptor)


def atomic_publish(
    data: bytes,
    *,
    final_path: Path,
    temporary_directory: Path,
    verify_file: Callable[[Path], None],
    fault_hook: FaultHook | None = None,
    on_temporary_created: Callable[[Path], None] | None = None,
    on_temporary_finished: Callable[[Path], None] | None = None,
) -> bool:
    temporary = temporary_directory / f"r3tmp-{uuid.uuid4().hex}.part"
    published = False
    if on_temporary_created is not None:
        on_temporary_created(temporary)
    try:
        with open(temporary, "xb", buffering=0) as stream:
            _fault(fault_hook, "F1", temporary, final_path)
            midpoint = len(data) // 2
            stream.write(data[:midpoint])
            _fault(fault_hook, "F2", temporary, final_path)
            stream.write(data[midpoint:])
            _fault(fault_hook, "F3", temporary, final_path)
            stream.flush()
            _fault(fault_hook, "F4", temporary, final_path)
            os.fsync(stream.fileno())
        verify_file(temporary)
        _fault(fault_hook, "F5", temporary, final_path)
        try:
            os.link(temporary, final_path)
            published = True
            fsync_directory(final_path.parent)
        except FileExistsError:
            published = False
        finally:
            temporary.unlink(missing_ok=True)
        _fault(fault_hook, "F6", temporary, final_path)
        verify_file(final_path)
        _fault(fault_hook, "F7", temporary, final_path)
        return published
    except Exception:
        temporary.unlink(missing_ok=True)
        raise
    finally:
        if on_temporary_finished is not None:
            on_temporary_finished(temporary)


def validate_existing_with_fault(
    final_path: Path, verify_file: Callable[[Path], None], fault_hook: FaultHook | None
) -> None:
    _fault(fault_hook, "F8", final_path, final_path)
    verify_file(final_path)
