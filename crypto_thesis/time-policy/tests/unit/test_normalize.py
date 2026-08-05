"""Unit tests for canonical interval normalization."""

import pytest

from time_policy.errors import InvalidIntervalError
from time_policy.models import Interval
from time_policy.normalize import normalize


def test_empty_input() -> None:
    assert normalize([]) == ()


def test_single_interval() -> None:
    assert normalize([Interval(2, 8)]) == (Interval(2, 8),)


def test_duplicate_intervals_are_removed() -> None:
    policy = [Interval(2, 8), Interval(2, 8)]
    assert normalize(policy) == (Interval(2, 8),)


def test_nested_intervals_are_merged() -> None:
    policy = [Interval(1, 10), Interval(3, 5), Interval(2, 9)]
    assert normalize(policy) == (Interval(1, 10),)


def test_adjacent_intervals_are_merged() -> None:
    policy = [Interval(1, 5), Interval(5, 8)]
    assert normalize(policy) == (Interval(1, 8),)


def test_chain_overlap_is_merged() -> None:
    policy = [Interval(1, 3), Interval(5, 7), Interval(2, 6)]
    assert normalize(policy) == (Interval(1, 7),)


def test_unordered_disjoint_intervals_are_sorted() -> None:
    policy = [Interval(8, 10), Interval(1, 3), Interval(12, 13)]
    assert normalize(policy) == (
        Interval(1, 3),
        Interval(8, 10),
        Interval(12, 13),
    )


def test_normalize_is_idempotent() -> None:
    policy = [
        Interval(8, 10),
        Interval(1, 4),
        Interval(3, 9),
        Interval(12, 13),
    ]
    once = normalize(policy)
    assert normalize(once) == once


def test_input_is_not_mutated() -> None:
    policy = [Interval(5, 8), Interval(1, 3)]
    original = list(policy)
    normalize(policy)
    assert policy == original


def test_domain_validation() -> None:
    with pytest.raises(InvalidIntervalError):
        normalize([Interval(0, 11)], domain_size=10)
    with pytest.raises(ValueError):
        normalize([], domain_size=0)
    with pytest.raises(TypeError):
        normalize([], domain_size=True)
