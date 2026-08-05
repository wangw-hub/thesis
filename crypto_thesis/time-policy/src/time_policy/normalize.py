"""Canonical normalization of unordered and redundant interval sequences."""

from __future__ import annotations

from collections.abc import Iterable

from .errors import InvalidIntervalError
from .models import Interval


def normalize(
    intervals: Iterable[Interval], *, domain_size: int | None = None
) -> tuple[Interval, ...]:
    """Return the unique ordered maximal interval representation.

    Overlapping, adjacent, duplicate, and nested intervals are merged. The
    input is not mutated.

    Args:
        intervals: Integer half-open intervals.
        domain_size: Optional exclusive upper bound used for validation.

    Raises:
        ValueError: If ``domain_size`` is not positive.
        InvalidIntervalError: If an interval exceeds ``domain_size``.
    """

    if domain_size is not None:
        if isinstance(domain_size, bool) or not isinstance(domain_size, int):
            raise TypeError("domain_size must be an int")
        if domain_size <= 0:
            raise ValueError("domain_size must be positive")

    ordered = sorted(intervals)
    if domain_size is not None:
        for interval in ordered:
            if interval.right > domain_size:
                raise InvalidIntervalError(
                    f"interval {interval} exceeds domain_size={domain_size}"
                )
    if not ordered:
        return ()

    merged: list[Interval] = []
    current_left = ordered[0].left
    current_right = ordered[0].right

    for interval in ordered[1:]:
        if interval.left <= current_right:
            # Equality merges adjacent half-open intervals.
            current_right = max(current_right, interval.right)
            continue
        merged.append(Interval(current_left, current_right))
        current_left, current_right = interval.left, interval.right

    merged.append(Interval(current_left, current_right))
    return tuple(merged)
