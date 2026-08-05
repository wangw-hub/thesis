"""Canonical CAP1 serialization."""

from __future__ import annotations

import struct

from .errors import TokenDecodeError
from .models import CapabilityPayload, ChainBinding, MatchedNode, Operation

MAGIC_V1 = b"CAP1"
MAGIC_V2 = b"CAP2"
_U16 = struct.Struct(">H")
_U64 = struct.Struct(">Q")


def _text(value: str) -> bytes:
    encoded = value.encode("utf-8")
    return _U16.pack(len(encoded)) + encoded


def encode_capability(payload: CapabilityPayload) -> bytes:
    """Encode a payload into its unique CAP1 byte representation."""

    flags = 1 if payload.matched_node is not None else 0
    parts = [
        MAGIC_V1 if payload.version == 1 else MAGIC_V2,
        bytes((payload.version, flags)),
        _text(payload.issuer),
        _text(payload.resource_id),
        payload.policy_digest,
        _U64.pack(payload.epoch),
        payload.user_key_id,
        bytes((int(payload.operation),)),
        _U64.pack(payload.not_before),
        _U64.pack(payload.expires_at),
        payload.nonce,
        _U64.pack(payload.issued_at),
    ]
    if payload.chain_binding is not None:
        parts.extend(
            (
                _U64.pack(payload.chain_binding.chain_id),
                payload.chain_binding.contract_address,
                _U64.pack(payload.chain_binding.resource_state_version),
                _U64.pack(payload.chain_binding.user_version),
            )
        )
    if payload.matched_node is not None:
        parts.extend(
            (
                _U64.pack(payload.matched_node.start),
                _U64.pack(payload.matched_node.size),
                payload.cover_version,
            )
        )
    return b"".join(parts)


class _Reader:
    def __init__(self, data: bytes) -> None:
        self.data = data
        self.offset = 0

    def take(self, size: int) -> bytes:
        end = self.offset + size
        if end > len(self.data):
            raise TokenDecodeError("truncated CAP1 input")
        value = self.data[self.offset:end]
        self.offset = end
        return value

    def uint16(self) -> int:
        return _U16.unpack(self.take(2))[0]

    def uint64(self) -> int:
        return _U64.unpack(self.take(8))[0]

    def text(self) -> str:
        raw = self.take(self.uint16())
        try:
            value = raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise TokenDecodeError("invalid UTF-8 in CAP1") from exc
        if not value:
            raise TokenDecodeError("empty CAP1 text field")
        return value


def decode_capability(data: bytes) -> CapabilityPayload:
    """Decode CAP1 bytes and reject unknown, trailing, or non-canonical input."""

    if not isinstance(data, bytes):
        raise TokenDecodeError("CAP1 input must be bytes")
    reader = _Reader(data)
    magic = reader.take(4)
    if magic not in (MAGIC_V1, MAGIC_V2):
        raise TokenDecodeError("invalid CAP1 magic")
    schema, flags = reader.take(2)
    expected_schema = 1 if magic == MAGIC_V1 else 2
    if schema != expected_schema or flags not in (0, 1):
        raise TokenDecodeError("unsupported CAP1 schema or flags")
    try:
        issuer = reader.text()
        resource_id = reader.text()
        digest = reader.take(32)
        epoch = reader.uint64()
        user_key_id = reader.take(32)
        operation = Operation(reader.take(1)[0])
        not_before = reader.uint64()
        expires_at = reader.uint64()
        nonce = reader.take(16)
        issued_at = reader.uint64()
        chain_binding = None
        if schema == 2:
            chain_binding = ChainBinding(
                reader.uint64(),
                reader.take(20),
                reader.uint64(),
                reader.uint64(),
            )
        node = None
        cover_version = None
        if flags:
            node = MatchedNode(reader.uint64(), reader.uint64())
            cover_version = reader.take(32)
        if reader.offset != len(data):
            raise TokenDecodeError("trailing CAP1 bytes")
        payload = CapabilityPayload(
            version=schema,
            issuer=issuer,
            resource_id=resource_id,
            policy_digest=digest,
            epoch=epoch,
            user_key_id=user_key_id,
            operation=operation,
            not_before=not_before,
            expires_at=expires_at,
            nonce=nonce,
            issued_at=issued_at,
            chain_binding=chain_binding,
            matched_node=node,
            cover_version=cover_version,
        )
    except (ValueError, IndexError) as exc:
        if isinstance(exc, TokenDecodeError):
            raise
        raise TokenDecodeError("invalid CAP1 field") from exc
    if encode_capability(payload) != data:
        raise TokenDecodeError("non-canonical CAP1 encoding")
    return payload
