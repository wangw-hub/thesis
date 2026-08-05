"""Boundary and large-domain correctness tests."""

from datetime import UTC, datetime, timedelta

from time_policy.compiler import compile_policy
from time_policy.matcher import dyadic_matcher, match
from time_policy.models import DyadicNode, Interval

ORIGIN = datetime(2026, 1, 1, tzinfo=UTC)
DELTA = timedelta(minutes=1)


def compile_for(intervals: list[Interval], domain_size: int):
    return compile_policy(
        intervals,
        time_origin=ORIGIN,
        delta=DELTA,
        domain_size=domain_size,
    )


def test_full_power_of_two_domain_has_one_cover_node() -> None:
    compiled = compile_for([Interval(0, 1024)], 1024)
    assert compiled.cover == (DyadicNode(0, 1024),)


def test_full_non_power_of_two_domain_uses_binary_decomposition() -> None:
    compiled = compile_for([Interval(0, 10)], 10)
    assert compiled.cover == (DyadicNode(0, 8), DyadicNode(8, 2))


def test_maximally_fragmented_even_slots_do_not_fake_compression() -> None:
    domain_size = 128
    raw = [Interval(slot, slot + 1) for slot in range(0, domain_size, 2)]
    compiled = compile_for(raw, domain_size)
    assert len(compiled.intervals) == domain_size // 2
    assert len(compiled.cover) == domain_size // 2


def test_large_domain_does_not_require_domain_sized_cover() -> None:
    domain_size = 1_000_000
    compiled = compile_for(
        [Interval(1, 10), Interval(500_000, 900_000)], domain_size
    )
    policy = dyadic_matcher(compiled.cover, domain_size)
    assert match(policy, 1)
    assert match(policy, 899_999)
    assert not match(policy, 10)
    assert not match(policy, 999_999)
    assert len(compiled.cover) < 100
