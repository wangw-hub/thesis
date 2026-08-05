from dataclasses import dataclass
from enum import Enum


class FailureCode(str, Enum):
    NONE = "NONE"
    INVALID_REFERENCE = "INVALID_REFERENCE"
    UNSUPPORTED_SCHEMA = "UNSUPPORTED_SCHEMA"
    UNSUPPORTED_BACKEND = "UNSUPPORTED_BACKEND"
    UNSUPPORTED_DIGEST_ALGORITHM = "UNSUPPORTED_DIGEST_ALGORITHM"
    INVALID_NAMESPACE = "INVALID_NAMESPACE"
    INVALID_DIGEST = "INVALID_DIGEST"
    OBJECT_NOT_FOUND = "OBJECT_NOT_FOUND"
    NOT_REGULAR_FILE = "NOT_REGULAR_FILE"
    SYMLINK_REJECTED = "SYMLINK_REJECTED"
    SIZE_MISMATCH = "SIZE_MISMATCH"
    DIGEST_MISMATCH = "DIGEST_MISMATCH"
    PATH_ESCAPE = "PATH_ESCAPE"
    READ_ERROR = "READ_ERROR"
    CORRUPT_OBJECT = "CORRUPT_OBJECT"


@dataclass(frozen=True)
class ObjectVerificationResult:
    reference_valid: bool = True
    exists: bool = False
    regular_file: bool = False
    symlink_rejected: bool = False
    size_matches: bool = False
    digest_matches: bool = False
    verified: bool = False
    failure_code: FailureCode = FailureCode.NONE
