"""Unit tests for immutable core data models."""

from datetime import UTC, datetime, timedelta
from hashlib import sha256

import pytest

from time_policy.models import CompiledPolicy, DyadicNode, Interval


def test_interval_is_half_open_and_immutable() -> None:
    interval = Interval(2, 5)
    assert interval.length == 3
    assert interval.contains(2)
    assert not interval.contains(5)
    with pytest.raises(AttributeError):
        interval.left = 1  # type: ignore[misc]


@pytest.mark.parametrize("left,right", [(-1, 2), (2, 2), (3, 2)])
def test_interval_rejects_invalid_bounds(left: int, right: int) -> None:
    with pytest.raises(ValueError):
        Interval(left, right)


@pytest.mark.parametrize("left,right", [(True, 2), (0, False), ("0", 2)])
def test_interval_rejects_non_integer_bounds(left, right) -> None:
    with pytest.raises(TypeError):
        Interval(left, right)


def test_dyadic_node_enforces_power_of_two_alignment() -> None:
    assert DyadicNode(8, 4).end == 12
    assert DyadicNode(8, 4).contains(11)
    assert not DyadicNode(8, 4).contains(12)
    with pytest.raises(ValueError):
        DyadicNode(8, 3)
    with pytest.raises(ValueError):
        DyadicNode(6, 4)
    with pytest.raises(ValueError):
        DyadicNode(-1, 1)
    with pytest.raises(TypeError):
        DyadicNode("0", 1)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        DyadicNode(0, True)


def test_compiled_policy_checks_domain() -> None:
    with pytest.raises(ValueError, match="exceeds"):
        CompiledPolicy(
            time_origin=datetime(2026, 1, 1, tzinfo=UTC),
            delta=timedelta(minutes=1),
            domain_size=4,
            intervals=(Interval(0, 5),),
            cover=(),
            canonical_bytes=b"",
            digest=sha256(b"").digest(),
        )


def test_compiled_policy_rejects_invalid_metadata_and_cover() -> None:
    valid = {
        "time_origin": datetime(2026, 1, 1, tzinfo=UTC),
        "delta": timedelta(minutes=1),
        "domain_size": 4,
        "intervals": (),
        "cover": (),
        "canonical_bytes": b"",
        "digest": sha256(b"").digest(),
    }
    for field, value in (
        ("time_origin", datetime(2026, 1, 1)),
        ("delta", timedelta(0)),
        ("domain_size", 0),
        ("digest", b"short"),
        ("digest", b"\x00" * 32),
        ("cover", (DyadicNode(4, 1),)),
    ):
        arguments = dict(valid)
        arguments[field] = value
        with pytest.raises(ValueError):
            CompiledPolicy(**arguments)
