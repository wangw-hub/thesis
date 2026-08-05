from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass
from typing import Any, Callable

from .agent import PlannedResourceUpdate
from .events import NormalizedAuthorizationEventV1


@dataclass(frozen=True)
class HeaderUpdateIntentV1:
    """Immutable authorization target carried from event scan to the worker."""

    schemaVersion: int
    resourceId: str
    eventId: str
    eventType: str
    updateKind: str
    targetEpoch: int
    targetStateVersion: int
    authorizationBlockNumber: int
    authorizationBlockHash: str
    sourceEventTxHash: str
    sourceEventLogIndex: int

    def __post_init__(self) -> None:
        if self.schemaVersion != 1:
            raise ValueError("UNSUPPORTED_HEADER_UPDATE_INTENT_SCHEMA")
        if self.updateKind != "HEADER_ONLY":
            raise ValueError("HEADER_UPDATE_INTENT_KIND_MISMATCH")
        if self.targetEpoch < 1 or self.targetStateVersion < 1:
            raise ValueError("INVALID_HEADER_UPDATE_TARGET_STATE")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "HeaderUpdateIntentV1":
        return cls(**value)


def header_update_intent_v1(
    event: NormalizedAuthorizationEventV1,
    plan: PlannedResourceUpdate,
) -> HeaderUpdateIntentV1:
    if event.event_name != "EpochAdvanced" or plan.update_kind.value != "HEADER_ONLY":
        raise RuntimeError("A7_EVENT_UPDATE_KIND_MISMATCH")
    if event.resource_id != plan.resource_id:
        raise RuntimeError("A7_EVENT_RESOURCE_MISMATCH")
    event_epoch = int(event.payload.get("newEpoch", -1))
    if event_epoch != plan.target_epoch:
        raise RuntimeError("A7_EVENT_FIXED_STATE_MISMATCH")
    event_id = hashlib.sha256(
        f"{event.chain_id}:{event.contract_address}:{event.transaction_hash}:{event.log_index}".encode()
    ).hexdigest()
    return HeaderUpdateIntentV1(
        1, plan.resource_id, event_id, event.event_name, plan.update_kind.value,
        plan.target_epoch, plan.target_state_version, event.block_number,
        event.block_hash, event.transaction_hash, event.log_index,
    )


def build_header_only_anchor_from_intent(
    anchor_factory: Callable[..., tuple[Any, ...]], intent: HeaderUpdateIntentV1,
    *, resource: bytes, policy: bytes, operation: bytes, header_version: int,
    body_version: int, key_version: int, previous_header_digest: bytes,
    header_digest: bytes, header_object_digest: bytes, body_object_digest: bytes,
) -> tuple[Any, ...]:
    if resource.hex() != intent.resourceId:
        raise RuntimeError("HEADER_UPDATE_INTENT_RESOURCE_MISMATCH")
    return anchor_factory(
        resource, policy, operation, header_version, body_version, key_version, 1,
        previous_header_digest, header_digest, header_object_digest, body_object_digest,
        epoch=intent.targetEpoch, state_version=intent.targetStateVersion,
    )
