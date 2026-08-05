"""Unit tests for compiler orchestration and semantic digests."""

from datetime import UTC, datetime, timedelta

import pytest

from time_policy.compiler import compile_policy
from time_policy.digest import policy_digest
from time_policy.errors import TimezoneRequiredError
from time_policy.models import Interval

ORIGIN = datetime(2026, 1, 1, tzinfo=UTC)
DELTA = timedelta(minutes=1)


def compile_example(intervals: list[Interval]):
    return compile_policy(
        intervals,
        time_origin=ORIGIN,
        delta=DELTA,
        domain_size=32,
    )


def test_compiler_returns_all_representations() -> None:
    compiled = compile_example([Interval(8, 10), Interval(1, 4)])
    assert compiled.intervals == (Interval(1, 4), Interval(8, 10))
    assert compiled.cover
    assert compiled.canonical_bytes.startswith(b"NTP1")
    assert policy_digest(compiled) == compiled.digest


def test_digest_is_invariant_to_order_duplicates_and_equivalent_splits() -> None:
    policies = [
        [Interval(1, 8), Interval(10, 12)],
        [Interval(10, 12), Interval(1, 8)],
        [Interval(1, 8), Interval(1, 8), Interval(10, 12)],
        [Interval(1, 3), Interval(3, 8), Interval(10, 11), Interval(11, 12)],
    ]
    compiled = [compile_example(policy) for policy in policies]
    assert len({item.canonical_bytes for item in compiled}) == 1
    assert len({item.digest for item in compiled}) == 1


def test_digest_changes_when_semantics_change() -> None:
    first = compile_example([Interval(1, 8)])
    second = compile_example([Interval(1, 9)])
    assert first.digest != second.digest


def test_compiler_requires_aware_origin() -> None:
    with pytest.raises(TimezoneRequiredError):
        compile_policy(
            [],
            time_origin=datetime(2026, 1, 1),
            delta=DELTA,
            domain_size=32,
        )
