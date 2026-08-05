class DatabaseBoundaryError(RuntimeError):
    pass


class ConflictingDuplicateError(DatabaseBoundaryError):
    pass


class StaleWriteRejected(DatabaseBoundaryError):
    pass


class InvalidTransition(DatabaseBoundaryError):
    pass


class CursorConflict(DatabaseBoundaryError):
    pass


class InvariantViolation(DatabaseBoundaryError):
    pass
