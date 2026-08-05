from __future__ import annotations

import hashlib
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from epoch_auth_r3.serialization.jcs_adapter import canonicalize


class EventClass(StrEnum):
    DIRECT_RESOURCE = "DIRECT_RESOURCE"
    USER_SCOPE = "USER_SCOPE"
    AUDIT_ONLY = "AUDIT_ONLY"


AUTHORIZATION_EVENT_MANIFEST = {
    "ResourceRegistered": EventClass.AUDIT_ONLY,
    "PolicyUpdated": EventClass.DIRECT_RESOURCE,
    "EpochAdvanced": EventClass.DIRECT_RESOURCE,
    "ResourceStatusChanged": EventClass.DIRECT_RESOURCE,
    "UserRegistered": EventClass.AUDIT_ONLY,
    "UserKeyRotated": EventClass.USER_SCOPE,
    "UserStatusChanged": EventClass.USER_SCOPE,
    "RoleGranted": EventClass.AUDIT_ONLY,
    "RoleRevoked": EventClass.AUDIT_ONLY,
}


def _hex32(value: str | bytes, name: str) -> str:
    raw = value.hex() if isinstance(value, bytes) else value.removeprefix("0x")
    if len(raw) != 64 or any(c not in "0123456789abcdef" for c in raw):
        raise ValueError(f"invalid {name}")
    return raw


@dataclass(frozen=True)
class NormalizedAuthorizationEventV1:
    chain_id: int
    contract_address: str
    event_name: str
    event_signature: str
    transaction_hash: str
    log_index: int
    block_number: int
    block_hash: str
    event_class: EventClass
    resource_id: str | None
    user_id: str | None
    payload: dict[str, Any]
    payload_digest: str

    @property
    def identity(self) -> tuple[int, str, str, int]:
        return self.chain_id, self.contract_address, self.transaction_hash, self.log_index


def normalize_event(
    *,
    chain_id: int,
    contract_address: str,
    event_name: str,
    event_signature: str | bytes,
    transaction_hash: str | bytes,
    log_index: int,
    block_number: int,
    block_hash: str | bytes,
    args: dict[str, Any],
) -> NormalizedAuthorizationEventV1:
    if event_name not in AUTHORIZATION_EVENT_MANIFEST:
        raise ValueError("UNSUPPORTED_AUTHORIZATION_EVENT")
    event_class = AUTHORIZATION_EVENT_MANIFEST[event_name]
    payload = {
        key: ("0x" + value.hex() if isinstance(value, bytes) else value)
        for key, value in sorted(args.items())
    }
    payload_digest = hashlib.sha256(canonicalize(payload)).hexdigest()
    resource_id = args.get("resourceId")
    user_id = args.get("userId")
    return NormalizedAuthorizationEventV1(
        chain_id,
        contract_address.lower(),
        event_name,
        _hex32(event_signature, "event signature"),
        _hex32(transaction_hash, "transaction hash"),
        int(log_index),
        int(block_number),
        _hex32(block_hash, "block hash"),
        event_class,
        _hex32(resource_id, "resource id") if resource_id is not None else None,
        _hex32(user_id, "user id") if user_id is not None else None,
        payload,
        payload_digest,
    )
