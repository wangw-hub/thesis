"""Immutable data models used by the compiler."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from hashlib import sha256


@dataclass(frozen=True, slots=True, order=True)
class Interval:
    """A non-empty half-open interval over integer time slots."""

    left: int
    right: int

    def __post_init__(self) -> None:
        if isinstance(self.left, bool) or not isinstance(self.left, int):
            raise TypeError("left must be an int")
        if isinstance(self.right, bool) or not isinstance(self.right, int):
            raise TypeError("right must be an int")
        if self.left < 0:
            raise ValueError("left must be non-negative")
        if self.left >= self.right:
            raise ValueError("interval must satisfy left < right")

    @property
    def length(self) -> int:
        """Return the number of represented slots."""

        return self.right - self.left

    def contains(self, slot: int) -> bool:
        """Return whether *slot* belongs to the interval."""

        return self.left <= slot < self.right


@dataclass(frozen=True, slots=True, order=True)
class DyadicNode:
    """A power-of-two-sized interval aligned to its own size."""

    start: int
    size: int

    def __post_init__(self) -> None:
        if isinstance(self.start, bool) or not isinstance(self.start, int):
            raise TypeError("start must be an int")
        if isinstance(self.size, bool) or not isinstance(self.size, int):
            raise TypeError("size must be an int")
        if self.start < 0:
            raise ValueError("start must be non-negative")
        if self.size <= 0 or self.size & (self.size - 1):
            raise ValueError("size must be a positive power of two")
        if self.start % self.size != 0:
            raise ValueError("start must be aligned to size")

    @property
    def end(self) -> int:
        """Return the exclusive end slot."""

        return self.start + self.size

    def contains(self, slot: int) -> bool:
        """Return whether *slot* belongs to the node."""

        return self.start <= slot < self.end


@dataclass(frozen=True, slots=True)
class CompiledPolicy:
    """Complete immutable result returned by :func:`compile_policy`."""

    time_origin: datetime
    delta: timedelta
    domain_size: int
    intervals: tuple[Interval, ...]
    cover: tuple[DyadicNode, ...]
    canonical_bytes: bytes
    digest: bytes

    def __post_init__(self) -> None:
        if self.time_origin.tzinfo is None:
            raise ValueError("time_origin must be timezone-aware")
        if self.delta <= timedelta(0):
            raise ValueError("delta must be positive")
        if self.domain_size <= 0:
            raise ValueError("domain_size must be positive")
        if len(self.digest) != 32:
            raise ValueError("digest must contain 32 bytes")
        if sha256(self.canonical_bytes).digest() != self.digest:
            raise ValueError("digest does not match canonical_bytes")
        if any(interval.right > self.domain_size for interval in self.intervals):
            raise ValueError("interval exceeds domain_size")
        if any(node.end > self.domain_size for node in self.cover):
            raise ValueError("cover node exceeds domain_size")
