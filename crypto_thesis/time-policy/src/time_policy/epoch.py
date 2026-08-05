"""UTC normalization and deterministic mapping from datetimes to slots."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Literal

from .errors import InvalidIntervalError, TimezoneRequiredError
from .models import Interval

Rounding = Literal["floor", "ceil"]


def _require_aware(value: datetime, name: str) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise TimezoneRequiredError(f"{name} must be timezone-aware")
    return value.astimezone(UTC)


def _timedelta_microseconds(value: timedelta) -> int:
    return (
        value.days * 86_400_000_000
        + value.seconds * 1_000_000
        + value.microseconds
    )


def time_to_slot(
    value: datetime,
    *,
    origin: datetime,
    delta: timedelta,
    domain_size: int,
    rounding: Rounding = "floor",
    allow_endpoint: bool = False,
) -> int:
    """Map an aware datetime to a discrete slot index.

    Args:
        value: Time to map.
        origin: Aware UTC-normalizable start of the time domain.
        delta: Positive slot duration.
        domain_size: Number of slots in the domain.
        rounding: ``"floor"`` or ``"ceil"``.
        allow_endpoint: Allow the exclusive domain endpoint to map to
            ``domain_size``. This is intended for interval right endpoints.

    Raises:
        TimezoneRequiredError: If ``value`` or ``origin`` is timezone-naive.
        ValueError: If configuration or rounding mode is invalid.
        InvalidIntervalError: If the mapped value is outside the domain.
    """

    value_utc = _require_aware(value, "value")
    origin_utc = _require_aware(origin, "origin")
    delta_us = _timedelta_microseconds(delta)
    if delta_us <= 0:
        raise ValueError("delta must be positive")
    if isinstance(domain_size, bool) or not isinstance(domain_size, int):
        raise TypeError("domain_size must be an int")
    if domain_size <= 0:
        raise ValueError("domain_size must be positive")
    if rounding not in ("floor", "ceil"):
        raise ValueError("rounding must be 'floor' or 'ceil'")

    elapsed_us = _timedelta_microseconds(value_utc - origin_utc)
    slot = (
        elapsed_us // delta_us
        if rounding == "floor"
        else -(-elapsed_us // delta_us)
    )
    maximum = domain_size if allow_endpoint else domain_size - 1
    if slot < 0 or slot > maximum:
        raise InvalidIntervalError(
            f"time maps to slot {slot}, outside allowed range [0, {maximum}]"
        )
    return slot


def interval_to_slots(
    start: datetime,
    end: datetime,
    *,
    origin: datetime,
    delta: timedelta,
    domain_size: int,
) -> Interval:
    """Convert an aware real-time half-open interval to slot coordinates.

    The start is rounded down and the end is rounded up. This conservative
    policy includes every slot touched by the declared interval.
    """

    start_utc = _require_aware(start, "start")
    end_utc = _require_aware(end, "end")
    if start_utc >= end_utc:
        raise InvalidIntervalError("interval must satisfy start < end")

    left = time_to_slot(
        start_utc,
        origin=origin,
        delta=delta,
        domain_size=domain_size,
        rounding="floor",
    )
    right = time_to_slot(
        end_utc,
        origin=origin,
        delta=delta,
        domain_size=domain_size,
        rounding="ceil",
        allow_endpoint=True,
    )
    if right > domain_size:
        raise InvalidIntervalError("interval end exceeds the time domain")
    return Interval(left, right)
