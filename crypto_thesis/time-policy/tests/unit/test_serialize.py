"""Unit tests for the NTP1 canonical binary format."""

from datetime import UTC, datetime, timedelta

import pytest

from time_policy.errors import SerializationError, TimezoneRequiredError
from time_policy.models import Interval
from time_policy.serialize import canonical_deserialize, canonical_serialize

ORIGIN = datetime(2026, 1, 1, tzinfo=UTC)


def test_ntp1_round_trip() -> None:
    intervals = (Interval(1, 4), Interval(8, 10))
    payload = canonical_serialize(
        time_origin=ORIGIN,
        delta=timedelta(minutes=1),
        domain_size=16,
        intervals=intervals,
    )
    decoded = canonical_deserialize(payload)
    assert payload[:4] == b"NTP1"
    assert decoded[:4] == (ORIGIN, timedelta(minutes=1), 16, intervals)
    assert decoded[4] == 1


def test_encoding_is_stable_and_fixed_width() -> None:
    payload = canonical_serialize(
        time_origin=ORIGIN,
        delta=timedelta(minutes=1),
        domain_size=16,
        intervals=(Interval(1, 4),),
    )
    assert payload.hex() == (
        "4e5450310001000000006955b900000000000000003c"
        "000000000000001000000001"
        "00000000000000010000000000000004"
    )


def test_serializer_rejects_noncanonical_intervals() -> None:
    with pytest.raises(SerializationError):
        canonical_serialize(
            time_origin=ORIGIN,
            delta=timedelta(minutes=1),
            domain_size=16,
            intervals=(Interval(4, 6), Interval(1, 2)),
        )
    with pytest.raises(SerializationError):
        canonical_serialize(
            time_origin=ORIGIN,
            delta=timedelta(minutes=1),
            domain_size=16,
            intervals=(Interval(1, 3), Interval(3, 5)),
        )


def test_serializer_rejects_subsecond_configuration() -> None:
    with pytest.raises(SerializationError):
        canonical_serialize(
            time_origin=ORIGIN,
            delta=timedelta(microseconds=1),
            domain_size=16,
            intervals=(),
        )


def test_decoder_rejects_wrong_magic_and_length() -> None:
    payload = canonical_serialize(
        time_origin=ORIGIN,
        delta=timedelta(minutes=1),
        domain_size=16,
        intervals=(),
    )
    with pytest.raises(SerializationError):
        canonical_deserialize(b"BAD!" + payload[4:])
    with pytest.raises(SerializationError):
        canonical_deserialize(payload + b"\x00")
    with pytest.raises(SerializationError):
        canonical_deserialize(b"NTP1")


def test_serializer_rejects_invalid_header_fields() -> None:
    common = {
        "time_origin": ORIGIN,
        "delta": timedelta(minutes=1),
        "domain_size": 16,
        "intervals": (),
    }
    with pytest.raises(TimezoneRequiredError):
        canonical_serialize(
            **{**common, "time_origin": datetime(2026, 1, 1)}
        )
    with pytest.raises(SerializationError):
        canonical_serialize(
            **{
                **common,
                "time_origin": ORIGIN.replace(microsecond=1),
            }
        )
    with pytest.raises(SerializationError):
        canonical_serialize(**{**common, "domain_size": 0})
    with pytest.raises(SerializationError):
        canonical_serialize(**common, schema=2**16)
    with pytest.raises(SerializationError):
        canonical_serialize(
            **{**common, "intervals": (Interval(0, 17),)}
        )
