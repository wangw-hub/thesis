"""Exhaustive semantic-policy checks for every bitmap with U <= 12."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from time_policy.compiler import compile_policy
from time_policy.matcher import (
    dyadic_matcher,
    enumerated_matcher,
    interval_matcher,
    match,
)
from time_policy.models import Interval

ORIGIN = datetime(2026, 1, 1, tzinfo=UTC)


def bitmap_intervals(mask: int, domain_size: int) -> list[Interval]:
    """Convert one semantic bitmap into maximal half-open intervals."""

    intervals: list[Interval] = []
    slot = 0
    while slot < domain_size:
        if not mask & (1 << slot):
            slot += 1
            continue
        left = slot
        while slot < domain_size and mask & (1 << slot):
            slot += 1
        intervals.append(Interval(left, slot))
    return intervals


@pytest.mark.exhaustive
@pytest.mark.parametrize("domain_size", range(1, 13))
def test_every_small_domain_semantic_policy(domain_size: int) -> None:
    for mask in range(1 << domain_size):
        intervals = bitmap_intervals(mask, domain_size)
        compiled = compile_policy(
            intervals,
            time_origin=ORIGIN,
            delta=timedelta(minutes=1),
            domain_size=domain_size,
        )
        policies = (
            enumerated_matcher(compiled.intervals, domain_size),
            interval_matcher(compiled.intervals, domain_size),
            dyadic_matcher(compiled.cover, domain_size),
        )
        for slot in range(domain_size):
            expected = bool(mask & (1 << slot))
            assert all(match(policy, slot) == expected for policy in policies)
