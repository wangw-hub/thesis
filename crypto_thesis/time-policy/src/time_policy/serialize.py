"""Canonical binary serialization for normalized time-policy semantics."""

from __future__ import annotations

import struct
from datetime import UTC, datetime, timedelta

from .errors import SerializationError, TimezoneRequiredError
from .models import Interval

MAGIC = b"NTP1"
SCHEMA_VERSION = 1
_HEADER = struct.Struct(">4sHqQQI")
_INTERVAL = struct.Struct(">QQ")


def canonical_serialize(
    *,
    time_origin: datetime,
    delta: timedelta,
    domain_size: int,
    intervals: tuple[Interval, ...],
    schema: int = SCHEMA_VERSION,
) -> bytes:
    """Serialize canonical semantic intervals into the ``NTP1`` format.

    The encoding is fixed-width and big-endian. JSON is deliberately excluded
    from the digest input.
    """

    if time_origin.tzinfo is None or time_origin.utcoffset() is None:
        raise TimezoneRequiredError("time_origin must be timezone-aware")
    origin_utc = time_origin.astimezone(UTC)
    if origin_utc.microsecond != 0:
        raise SerializationError("time_origin must align to whole seconds")
    delta_us = (
        delta.days * 86_400_000_000
        + delta.seconds * 1_000_000
        + delta.microseconds
    )
    if delta_us <= 0 or delta_us % 1_000_000 != 0:
        raise SerializationError("delta must be a positive whole number of seconds")
    delta_seconds = delta_us // 1_000_000
    if not 0 < domain_size < 2**64:
        raise SerializationError("domain_size must fit uint64 and be positive")
    if not 0 <= schema < 2**16:
        raise SerializationError("schema must fit uint16")
    if len(intervals) >= 2**32:
        raise SerializationError("interval count must fit uint32")

    previous_right = -1
    chunks = [
        _HEADER.pack(
            MAGIC,
            schema,
            int(origin_utc.timestamp()),
            delta_seconds,
            domain_size,
            len(intervals),
        )
    ]
    for interval in intervals:
        if interval.right > domain_size:
            raise SerializationError("interval exceeds domain_size")
        if interval.left <= previous_right:
            raise SerializationError(
                "intervals must be ordered, disjoint, and non-adjacent"
            )
        chunks.append(_INTERVAL.pack(interval.left, interval.right))
        previous_right = interval.right
    return b"".join(chunks)


def canonical_deserialize(
    payload: bytes,
) -> tuple[datetime, timedelta, int, tuple[Interval, ...], int]:
    """Decode and validate an ``NTP1`` canonical payload."""

    if len(payload) < _HEADER.size:
        raise SerializationError("payload is shorter than the NTP1 header")
    magic, schema, origin_s, delta_s, domain_size, count = _HEADER.unpack_from(
        payload
    )
    if magic != MAGIC:
        raise SerializationError("invalid NTP1 magic")
    expected_size = _HEADER.size + count * _INTERVAL.size
    if len(payload) != expected_size:
        raise SerializationError("payload length does not match interval count")

    intervals: list[Interval] = []
    offset = _HEADER.size
    for _ in range(count):
        left, right = _INTERVAL.unpack_from(payload, offset)
        intervals.append(Interval(left, right))
        offset += _INTERVAL.size

    normalized = tuple(intervals)
    # Reuse the encoder as the single source of canonical-order validation.
    if canonical_serialize(
        time_origin=datetime.fromtimestamp(origin_s, UTC),
        delta=timedelta(seconds=delta_s),
        domain_size=domain_size,
        intervals=normalized,
        schema=schema,
    ) != payload:
        raise SerializationError("payload is not canonical")
    return (
        datetime.fromtimestamp(origin_s, UTC),
        timedelta(seconds=delta_s),
        domain_size,
        normalized,
        schema,
    )
