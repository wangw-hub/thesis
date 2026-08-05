"""Unit tests for maximal dyadic interval covers."""

import pytest

from time_policy.cover import cover_policy, dyadic_cover
from time_policy.errors import InvalidIntervalError
from time_policy.models import DyadicNode, Interval


def expand(nodes: tuple[DyadicNode, ...]) -> set[int]:
    """Expand nodes for small-domain test assertions."""

    return {
        slot
        for node in nodes
        for slot in range(node.start, node.end)
    }


def test_aligned_power_of_two_interval_has_one_node() -> None:
    assert dyadic_cover(Interval(0, 8), 8) == (DyadicNode(0, 8),)
    assert dyadic_cover(Interval(8, 12), 16) == (DyadicNode(8, 4),)


def test_unaligned_interval_has_expected_maximal_cover() -> None:
    assert dyadic_cover(Interval(1, 15), 16) == (
        DyadicNode(1, 1),
        DyadicNode(2, 2),
        DyadicNode(4, 4),
        DyadicNode(8, 4),
        DyadicNode(12, 2),
        DyadicNode(14, 1),
    )


def test_non_power_of_two_domain_does_not_leak_past_boundary() -> None:
    nodes = dyadic_cover(Interval(0, 10), 10)
    assert nodes == (DyadicNode(0, 8), DyadicNode(8, 2))
    assert max(node.end for node in nodes) == 10


def test_cover_is_complete_non_overlapping_and_aligned() -> None:
    interval = Interval(3, 29)
    nodes = dyadic_cover(interval, 32)
    assert expand(nodes) == set(range(3, 29))
    assert all(node.size & (node.size - 1) == 0 for node in nodes)
    assert all(node.start % node.size == 0 for node in nodes)
    assert all(node.end <= 32 for node in nodes)
    assert all(a.end <= b.start for a, b in zip(nodes, nodes[1:]))


def test_every_node_is_maximal_within_source_interval() -> None:
    interval = Interval(3, 29)
    for node in dyadic_cover(interval, 32):
        parent_size = node.size * 2
        parent_start = node.start - (node.start % parent_size)
        parent_end = parent_start + parent_size
        assert not (
            interval.left <= parent_start and parent_end <= interval.right
        )


def test_cover_policy_preserves_gaps() -> None:
    intervals = (Interval(1, 4), Interval(8, 10))
    nodes = cover_policy(intervals, 16)
    assert expand(nodes) == {1, 2, 3, 8, 9}


def test_cover_policy_requires_canonical_interval_order() -> None:
    with pytest.raises(ValueError):
        cover_policy((Interval(4, 6), Interval(1, 2)), 8)
    with pytest.raises(ValueError):
        cover_policy((Interval(1, 3), Interval(3, 5)), 8)


def test_cover_rejects_out_of_domain_interval() -> None:
    with pytest.raises(InvalidIntervalError):
        dyadic_cover(Interval(8, 11), 10)
    with pytest.raises(TypeError):
        dyadic_cover(Interval(0, 1), True)
    with pytest.raises(ValueError):
        dyadic_cover(Interval(0, 1), 0)
