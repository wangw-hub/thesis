from typing import Protocol, runtime_checkable

from .references import ObjectKind, ObjectReferenceV1
from .verification import ObjectVerificationResult


@runtime_checkable
class StorageGateway(Protocol):
    def put(
        self,
        data: bytes,
        *,
        namespace: str,
        object_kind: ObjectKind,
        expected_digest: str | None = None,
    ) -> ObjectReferenceV1: ...

    def get(self, reference: ObjectReferenceV1) -> bytes: ...

    def exists(self, reference: ObjectReferenceV1) -> bool: ...

    def verify(self, reference: ObjectReferenceV1) -> ObjectVerificationResult: ...
