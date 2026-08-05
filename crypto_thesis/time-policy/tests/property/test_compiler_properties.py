"""High-volume property tests for compiler correctness."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from hypothesis import HealthCheck, given, settings

from time_policy.compiler import compile_policy
from time_policy.cover import cover_policy
from time_policy.matcher import (
    dyadic_matcher,
    enumerated_matcher,
    interval_matcher,
    match,
)
from time_policy.models import Interval
from time_policy.normalize import normalize

from .strategies import raw_policies

ORIGIN = datetime(2026, 1, 1, tzinfo=UTC)
DELTA = timedelta(minutes=1)


def raw_match(intervals: list[Interval], slot: int) -> bool:
    """Evaluate raw policy semantics directly."""

    return any(interval.contains(slot) for interval in intervals)


@settings(
    max_examples=10_000,
    deadline=None,
    suppress_health_check=(HealthCheck.too_slow,),
)
@given(raw_policies())
def test_compiler_semantics_and_invariants(
    policy_case: tuple[int, list[Interval]],
) -> None:
    domain_size, raw = policy_case
    compiled = compile_policy(
        raw,
        time_origin=ORIGIN,
        delta=DELTA,
        domain_size=domain_size,
    )

    # Normalize is a canonical fixed point and input order has no effect.
    assert normalize(compiled.intervals, domain_size=domain_size) == (
        compiled.intervals
    )
    reversed_compiled = compile_policy(
        list(reversed(raw)),
        time_origin=ORIGIN,
        delta=DELTA,
        domain_size=domain_size,
    )
    assert reversed_compiled.canonical_bytes == compiled.canonical_bytes
    assert reversed_compiled.digest == compiled.digest

    matchers = (
        enumerated_matcher(compiled.intervals, domain_size),
        interval_matcher(compiled.intervals, domain_size),
        dyadic_matcher(compiled.cover, domain_size),
    )
    for slot in range(domain_size):
        expected = raw_match(raw, slot)
        assert all(match(matcher, slot) == expected for matcher in matchers)

    # Every cover node is aligned, bounded, disjoint, and maximal.
    for index, node in enumerate(compiled.cover):
        assert node.size & (node.size - 1) == 0
        assert node.start % node.size == 0
        assert node.end <= domain_size
        if index:
            assert compiled.cover[index - 1].end <= node.start

        source = next(
            interval
            for interval in compiled.intervals
            if interval.left <= node.start and node.end <= interval.right
        )
        parent_size = node.size * 2
        parent_start = node.start - (node.start % parent_size)
        parent_end = parent_start + parent_size
        assert not (
            source.left <= parent_start and parent_end <= source.right
        )

    # Splitting a non-singleton canonical interval preserves bytes and digest.
    splittable = next(
        (interval for interval in compiled.intervals if interval.length > 1),
        None,
    )
    if splittable is not None:
        midpoint = splittable.left + splittable.length // 2
        split_raw = [
            interval
            for interval in compiled.intervals
            if interval != splittable
        ]
        split_raw.extend(
            [
                Interval(splittable.left, midpoint),
                Interval(midpoint, splittable.right),
            ]
        )
        split_compiled = compile_policy(
            split_raw,
            time_origin=ORIGIN,
            delta=DELTA,
            domain_size=domain_size,
        )
        assert split_compiled.canonical_bytes == compiled.canonical_bytes
        assert split_compiled.digest == compiled.digest


@settings(max_examples=500, deadline=None)
@given(raw_policies())
def test_duplicate_input_is_semantically_invariant(
    policy_case: tuple[int, list[Interval]],
) -> None:
    domain_size, raw = policy_case
    duplicate = raw + raw[: min(3, len(raw))]
    first = compile_policy(
        raw,
        time_origin=ORIGIN,
        delta=DELTA,
        domain_size=domain_size,
    )
    second = compile_policy(
        duplicate,
        time_origin=ORIGIN,
        delta=DELTA,
        domain_size=domain_size,
    )
    assert first.canonical_bytes == second.canonical_bytes
    assert first.digest == second.digest


@settings(max_examples=500, deadline=None)
@given(raw_policies())
def test_cover_function_agrees_with_compiler(
    policy_case: tuple[int, list[Interval]],
) -> None:
    domain_size, raw = policy_case
    normalized = normalize(raw, domain_size=domain_size)
    compiled = compile_policy(
        raw,
        time_origin=ORIGIN,
        delta=DELTA,
        domain_size=domain_size,
    )
    assert cover_policy(normalized, domain_size) == compiled.cover
