class StorageError(RuntimeError):
    """Base fail-closed storage error."""


class InvalidReferenceError(StorageError):
    pass


class DigestMismatchError(StorageError):
    pass


class CorruptObjectError(StorageError):
    pass


class PathSecurityError(StorageError):
    pass


class InjectedStorageFault(StorageError):
    """Raised only by the test fault-injection hook."""
