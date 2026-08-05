from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum

from epoch_auth_r3.serialization.jcs_adapter import canonicalize, parse_strict

from .exceptions import InvalidReferenceError

MAX_OBJECT_SIZE = 1 << 30
_NAMESPACE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
_DIGEST = re.compile(r"^[0-9a-f]{64}$")
_FIELDS = {
    "schemaVersion",
    "backend",
    "namespace",
    "objectKind",
    "digestAlgorithm",
    "digestHex",
    "sizeBytes",
}


class ObjectKind(str, Enum):
    BODY = "BODY"
    HEADER = "HEADER"
    GENERIC_TEST = "GENERIC_TEST"


def validate_namespace(value: object) -> str:
    if not isinstance(value, str) or not _NAMESPACE.fullmatch(value):
        raise InvalidReferenceError("INVALID_NAMESPACE")
    if value in {".", ".."} or ":" in value:
        raise InvalidReferenceError("INVALID_NAMESPACE")
    return value


def validate_digest(value: object) -> str:
    if not isinstance(value, str) or not _DIGEST.fullmatch(value):
        raise InvalidReferenceError("INVALID_DIGEST")
    return value


@dataclass(frozen=True)
class ObjectReferenceV1:
    schema_version: int
    backend: str
    namespace: str
    object_kind: ObjectKind
    digest_algorithm: str
    digest_hex: str
    size_bytes: int

    def __post_init__(self) -> None:
        if type(self.schema_version) is not int or self.schema_version != 1:
            raise InvalidReferenceError("UNSUPPORTED_SCHEMA")
        if self.backend != "local":
            raise InvalidReferenceError("UNSUPPORTED_BACKEND")
        validate_namespace(self.namespace)
        if not isinstance(self.object_kind, ObjectKind):
            raise InvalidReferenceError("INVALID_OBJECT_KIND")
        if self.digest_algorithm != "sha256":
            raise InvalidReferenceError("UNSUPPORTED_DIGEST_ALGORITHM")
        validate_digest(self.digest_hex)
        if (
            type(self.size_bytes) is not int
            or self.size_bytes < 0
            or self.size_bytes > MAX_OBJECT_SIZE
        ):
            raise InvalidReferenceError("INVALID_SIZE")

    def to_canonical_dict(self) -> dict:
        return {
            "backend": self.backend,
            "digestAlgorithm": self.digest_algorithm,
            "digestHex": self.digest_hex,
            "namespace": self.namespace,
            "objectKind": self.object_kind.value,
            "schemaVersion": self.schema_version,
            "sizeBytes": self.size_bytes,
        }

    @classmethod
    def from_strict_dict(cls, value: object) -> "ObjectReferenceV1":
        if not isinstance(value, dict) or set(value) != _FIELDS:
            raise InvalidReferenceError("INVALID_REFERENCE_FIELDS")
        try:
            kind = ObjectKind(value["objectKind"])
        except (ValueError, TypeError) as exc:
            raise InvalidReferenceError("INVALID_OBJECT_KIND") from exc
        return cls(
            value["schemaVersion"],
            value["backend"],
            value["namespace"],
            kind,
            value["digestAlgorithm"],
            value["digestHex"],
            value["sizeBytes"],
        )

    def to_canonical_bytes(self) -> bytes:
        return canonicalize(self.to_canonical_dict())

    @classmethod
    def from_strict_json(cls, value: str | bytes) -> "ObjectReferenceV1":
        try:
            return cls.from_strict_dict(parse_strict(value))
        except InvalidReferenceError:
            raise
        except (TypeError, ValueError) as exc:
            raise InvalidReferenceError("INVALID_REFERENCE_JSON") from exc

    def digest_identity(self) -> str:
        return f"sha256:{self.digest_hex}"
