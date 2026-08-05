"""Comparable matchers for enumerated, interval, and dyadic policies."""

from __future__ import annotations

from bisect import bisect_right
from dataclasses import dataclass
from typing import Protocol

from .models import DyadicNode, Interval


class PolicyMatcher(Protocol):
    """Structural protocol implemented by all policy matchers."""

    domain_size: int

    def match(self, slot: int) -> bool:
        """Return whether the slot is allowed."""


def _validate_query(slot: int, domain_size: int) -> None:
    if isinstance(slot, bool) or not isinstance(slot, int):
        raise TypeError("slot must be an int")
    if not 0 <= slot < domain_size:
        raise ValueError(f"slot must be in [0, {domain_size})")


@dataclass(frozen=True, slots=True)
class EnumeratedMatcher:
    """Baseline matcher backed by an explicit set of allowed slots."""

    domain_size: int
    slots: frozenset[int]

    def match(self, slot: int) -> bool:
        """Return membership using expected constant-time set lookup."""

        _validate_query(slot, self.domain_size)
        return slot in self.slots


@dataclass(frozen=True, slots=True)
class IntervalMatcher:
    """Baseline matcher backed by canonical intervals and binary search."""

    domain_size: int
    intervals: tuple[Interval, ...]
    left_endpoints: tuple[int, ...]

    def match(self, slot: int) -> bool:
        """Return membership using binary search over interval starts."""

        _validate_query(slot, self.domain_size)
        index = bisect_right(self.left_endpoints, slot) - 1
        return index >= 0 and self.intervals[index].contains(slot)


@dataclass(frozen=True, slots=True)
class DyadicMatcher:
    """Matcher backed by dyadic nodes indexed by ``(start, size)``."""

    domain_size: int
    nodes: frozenset[tuple[int, int]]
    tree_capacity: int

    def match(self, slot: int) -> bool:
        """Return membership by checking the leaf-to-root ancestor path."""

        _validate_query(slot, self.domain_size)
        size = 1
        while size <= self.tree_capacity:
            start = slot & ~(size - 1)
            if (start, size) in self.nodes:
                return True
            size <<= 1
        return False


def enumerated_matcher(
    intervals: tuple[Interval, ...], domain_size: int
) -> EnumeratedMatcher:
    """Build the explicit-slot baseline matcher."""

    slots = frozenset(
        slot
        for interval in intervals
        for slot in range(interval.left, interval.right)
    )
    return EnumeratedMatcher(domain_size=domain_size, slots=slots)


def interval_matcher(
    intervals: tuple[Interval, ...], domain_size: int
) -> IntervalMatcher:
    """Build the canonical interval-list baseline matcher."""

    return IntervalMatcher(
        domain_size=domain_size,
        intervals=intervals,
        left_endpoints=tuple(interval.left for interval in intervals),
    )


def dyadic_matcher(
    nodes: tuple[DyadicNode, ...], domain_size: int
) -> DyadicMatcher:
    """Build the hierarchical dyadic matcher."""

    if domain_size <= 0:
        raise ValueError("domain_size must be positive")
    capacity = 1 << (domain_size - 1).bit_length()
    return DyadicMatcher(
        domain_size=domain_size,
        nodes=frozenset((node.start, node.size) for node in nodes),
        tree_capacity=capacity,
    )


def match(policy: PolicyMatcher, slot: int) -> bool:
    """Match a slot through the common policy interface."""

    return policy.match(slot)
