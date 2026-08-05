"""Unit tests for the three comparable policy matchers."""

import pytest

from time_policy.cover import cover_policy
from time_policy.matcher import (
    dyadic_matcher,
    enumerated_matcher,
    interval_matcher,
    match,
)
from time_policy.models import Interval


def test_all_matchers_have_identical_semantics() -> None:
    domain_size = 16
    intervals = (Interval(1, 4), Interval(8, 15))
    policies = (
        enumerated_matcher(intervals, domain_size),
        interval_matcher(intervals, domain_size),
        dyadic_matcher(cover_policy(intervals, domain_size), domain_size),
    )
    expected = {1, 2, 3, 8, 9, 10, 11, 12, 13, 14}
    for slot in range(domain_size):
        assert {match(policy, slot) for policy in policies} == {
            slot in expected
        }


def test_empty_policy_matches_nothing() -> None:
    policies = (
        enumerated_matcher((), 8),
        interval_matcher((), 8),
        dyadic_matcher((), 8),
    )
    assert all(not match(policy, 0) for policy in policies)


@pytest.mark.parametrize("slot", [-1, 8])
def test_match_rejects_out_of_domain_queries(slot: int) -> None:
    policy = interval_matcher((Interval(1, 3),), 8)
    with pytest.raises(ValueError):
        match(policy, slot)


def test_match_rejects_non_integer_query() -> None:
    policy = interval_matcher((Interval(1, 3),), 8)
    with pytest.raises(TypeError):
        match(policy, True)


def test_dyadic_matcher_finds_large_ancestor_node() -> None:
    policy = dyadic_matcher(cover_policy((Interval(0, 8),), 16), 16)
    assert match(policy, 7)
    assert not match(policy, 8)


def test_dyadic_matcher_rejects_invalid_domain() -> None:
    with pytest.raises(ValueError):
        dyadic_matcher((), 0)
