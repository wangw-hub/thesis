from __future__ import annotations

import base64
import re
from dataclasses import dataclass

from .exceptions import InvalidCidError

_CID = re.compile(r"^b[a-z2-7]{58}$")


def _varint(data: bytes, offset: int) -> tuple[int, int]:
    value = 0
    for shift in range(0, 64, 7):
        if offset >= len(data):
            raise InvalidCidError("TRUNCATED_CID")
        byte = data[offset]
        offset += 1
        value |= (byte & 0x7F) << shift
        if not byte & 0x80:
            return value, offset
    raise InvalidCidError("INVALID_VARINT")


@dataclass(frozen=True)
class ParsedCidV1:
    text: str
    version: int
    codec: int
    multihash_code: int
    digest: bytes


def parse_cid_v1(value: str) -> ParsedCidV1:
    if not isinstance(value, str) or not _CID.fullmatch(value):
        raise InvalidCidError("INVALID_CID_TEXT")
    try:
        encoded = value[1:].upper()
        encoded += "=" * ((8 - len(encoded) % 8) % 8)
        payload = base64.b32decode(encoded)
    except ValueError as exc:
        raise InvalidCidError("INVALID_CID_BASE32") from exc
    version, offset = _varint(payload, 0)
    codec, offset = _varint(payload, offset)
    code, offset = _varint(payload, offset)
    length, offset = _varint(payload, offset)
    digest = payload[offset:]
    # The frozen add profile uses raw leaves. A single-leaf object therefore
    # has the raw codec (0x55), while a chunked object has a dag-pb root (0x70).
    if version != 1 or codec not in {0x55, 0x70} or code != 0x12 or length != 32 or len(digest) != 32:
        raise InvalidCidError("UNSUPPORTED_CID_PROFILE")
    return ParsedCidV1(value, version, codec, code, digest)
