"""Maximal dyadic decomposition of normalized time intervals."""

from __future__ import annotations

from collections.abc import Iterable

from .errors import InvalidIntervalError
from .models import DyadicNode, Interval


def _highest_power_of_two_at_most(value: int) -> int:
    return 1 << (value.bit_length() - 1)


def dyadic_cover(
    interval: Interval, domain_size: int
) -> tuple[DyadicNode, ...]:
    """Return the ordered maximal dyadic cover of one interval.

    The algorithm emits one maximal aligned power-of-two block at a time and
    uses integer bit operations only.
    """

    if isinstance(domain_size, bool) or not isinstance(domain_size, int):
        raise TypeError("domain_size must be an int")
    if domain_size <= 0:
        raise ValueError("domain_size must be positive")
    if interval.right > domain_size:
        raise InvalidIntervalError(
            f"interval {interval} exceeds domain_size={domain_size}"
        )

    nodes: list[DyadicNode] = []
    left = interval.left
    right = interval.right

    while left < right:
        remaining = right - left
        if left == 0:
            size = _highest_power_of_two_at_most(remaining)
        else:
            # The least significant set bit is the largest block aligned at
            # this start. Shrink it if the right boundary is closer.
            size = left & -left
            while size > remaining:
                size >>= 1
        nodes.append(DyadicNode(start=left, size=size))
        left += size

    return tuple(nodes)


def cover_policy(
    intervals: Iterable[Interval], domain_size: int
) -> tuple[DyadicNode, ...]:
    """Return the ordered dyadic cover of normalized disjoint intervals."""

    nodes: list[DyadicNode] = []
    previous_right = -1
    for interval in intervals:
        if interval.left <= previous_right:
            raise ValueError(
                "intervals must be ordered, disjoint, and non-adjacent"
            )
        nodes.extend(dyadic_cover(interval, domain_size))
        previous_right = interval.right
    return tuple(nodes)
