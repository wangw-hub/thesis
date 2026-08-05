"""Unit tests for UTC and slot conversion."""

from datetime import UTC, datetime, timedelta, timezone

import pytest

from time_policy.epoch import interval_to_slots, time_to_slot
from time_policy.errors import InvalidIntervalError, TimezoneRequiredError
from time_policy.models import Interval

ORIGIN = datetime(2026, 1, 1, tzinfo=UTC)
DELTA = timedelta(minutes=1)


def test_time_to_slot_normalizes_timezone_offsets() -> None:
    utc_value = datetime(2026, 1, 1, 0, 5, tzinfo=UTC)
    offset_value = datetime(
        2026, 1, 1, 8, 5, tzinfo=timezone(timedelta(hours=8))
    )
    assert time_to_slot(
        utc_value, origin=ORIGIN, delta=DELTA, domain_size=10
    ) == time_to_slot(
        offset_value, origin=ORIGIN, delta=DELTA, domain_size=10
    )


@pytest.mark.parametrize(
    "seconds,rounding,expected",
    [(0, "floor", 0), (59, "floor", 0), (60, "floor", 1), (1, "ceil", 1)],
)
def test_time_to_slot_rounding(
    seconds: int, rounding: str, expected: int
) -> None:
    assert (
        time_to_slot(
            ORIGIN + timedelta(seconds=seconds),
            origin=ORIGIN,
            delta=DELTA,
            domain_size=10,
            rounding=rounding,  # type: ignore[arg-type]
        )
        == expected
    )


def test_interval_conversion_uses_half_open_conservative_rounding() -> None:
    result = interval_to_slots(
        ORIGIN + timedelta(seconds=30),
        ORIGIN + timedelta(minutes=2, seconds=1),
        origin=ORIGIN,
        delta=DELTA,
        domain_size=10,
    )
    assert result == Interval(0, 3)


def test_interval_can_end_at_exclusive_domain_endpoint() -> None:
    result = interval_to_slots(
        ORIGIN + timedelta(minutes=9),
        ORIGIN + timedelta(minutes=10),
        origin=ORIGIN,
        delta=DELTA,
        domain_size=10,
    )
    assert result == Interval(9, 10)


def test_timezone_is_required() -> None:
    with pytest.raises(TimezoneRequiredError):
        time_to_slot(
            datetime(2026, 1, 1),
            origin=ORIGIN,
            delta=DELTA,
            domain_size=10,
        )


@pytest.mark.parametrize(
    "start,end",
    [
        (ORIGIN, ORIGIN),
        (ORIGIN + timedelta(minutes=2), ORIGIN + timedelta(minutes=1)),
    ],
)
def test_interval_rejects_empty_or_reversed_range(
    start: datetime, end: datetime
) -> None:
    with pytest.raises(InvalidIntervalError):
        interval_to_slots(
            start, end, origin=ORIGIN, delta=DELTA, domain_size=10
        )


def test_interval_rejects_out_of_domain_values() -> None:
    with pytest.raises(InvalidIntervalError):
        interval_to_slots(
            ORIGIN - timedelta(seconds=1),
            ORIGIN + timedelta(minutes=1),
            origin=ORIGIN,
            delta=DELTA,
            domain_size=10,
        )
    with pytest.raises(InvalidIntervalError):
        interval_to_slots(
            ORIGIN + timedelta(minutes=9),
            ORIGIN + timedelta(minutes=11),
            origin=ORIGIN,
            delta=DELTA,
            domain_size=10,
        )


def test_invalid_configuration_is_rejected() -> None:
    with pytest.raises(ValueError):
        time_to_slot(
            ORIGIN, origin=ORIGIN, delta=timedelta(0), domain_size=10
        )
    with pytest.raises(ValueError):
        time_to_slot(ORIGIN, origin=ORIGIN, delta=DELTA, domain_size=0)
    with pytest.raises(TypeError):
        time_to_slot(
            ORIGIN, origin=ORIGIN, delta=DELTA, domain_size=True
        )
    with pytest.raises(ValueError):
        time_to_slot(
            ORIGIN,
            origin=ORIGIN,
            delta=DELTA,
            domain_size=10,
            rounding="nearest",  # type: ignore[arg-type]
        )
