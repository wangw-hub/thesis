"""Fair cache primitives for Baseline-I and Proposed-C experiments."""

from __future__ import annotations

import time
from collections import OrderedDict
from dataclasses import dataclass
from threading import RLock
from typing import Callable, Generic, Hashable, TypeVar

from time_policy.models import CompiledPolicy

from .baseline_i import BaselineIExecutor, PolicyMatch, _slot_at
from .proposed_c import ProposedCExecutor

T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class AuthorizationCacheContext:
    """Security context shared by interval-level and node-level cache keys."""

    chain_id: int
    contract_address: bytes
    resource_id: str
    policy_digest: bytes
    epoch: int
    state_version: int
    user_key_id: bytes
    user_version: int
    operation: int


@dataclass(frozen=True, slots=True)
class AuthorizationCacheKey:
    """One context-bound cache key with an interval or dyadic segment."""

    context: AuthorizationCacheContext
    segment_kind: str
    segment_start: int
    segment_size: int
    cover_version: bytes | None = None


@dataclass(frozen=True, slots=True)
class CacheStats:
    """Immutable cache counters used by the experiment recorder."""

    hits: int
    misses: int
    evictions: int
    invalidations: int
    entries: int


@dataclass(frozen=True, slots=True)
class CacheLookupResult(Generic[T]):
    """The result of exactly one cache lookup."""

    hit: bool
    value: T | None
    size_before: int
    size_after: int


class LruTtlCache(Generic[T]):
    """Thread-safe fixed-capacity LRU cache with one frozen TTL policy."""

    def __init__(
        self,
        capacity: int,
        ttl_ns: int,
        *,
        clock: Callable[[], int] = time.monotonic_ns,
    ) -> None:
        if capacity <= 0 or ttl_ns <= 0:
            raise ValueError("capacity and ttl_ns must be positive")
        self.capacity = capacity
        self.ttl_ns = ttl_ns
        self._clock = clock
        self._items: OrderedDict[Hashable, tuple[int, T]] = OrderedDict()
        self._hits = 0
        self._misses = 0
        self._evictions = 0
        self._invalidations = 0
        self._lock = RLock()

    def lookup(self, key: Hashable) -> CacheLookupResult[T]:
        """Return an explicit per-lookup result without counter inference."""

        now = self._clock()
        with self._lock:
            size_before = len(self._items)
            item = self._items.get(key)
            if item is None:
                self._misses += 1
                return CacheLookupResult(False, None, size_before, len(self._items))
            expires_at, value = item
            if expires_at <= now:
                del self._items[key]
                self._invalidations += 1
                self._misses += 1
                return CacheLookupResult(False, None, size_before, len(self._items))
            self._items.move_to_end(key)
            self._hits += 1
            return CacheLookupResult(True, value, size_before, len(self._items))

    def get(self, key: Hashable) -> T | None:
        """Compatibility wrapper around :meth:`lookup`."""

        return self.lookup(key).value

    def put(self, key: Hashable, value: T) -> None:
        """Insert or replace one entry under the common LRU policy."""

        with self._lock:
            self._items[key] = (self._clock() + self.ttl_ns, value)
            self._items.move_to_end(key)
            while len(self._items) > self.capacity:
                self._items.popitem(last=False)
                self._evictions += 1

    def invalidate_context(self, context: AuthorizationCacheContext) -> int:
        """Remove entries for one exact authorization-state context."""

        with self._lock:
            keys = [
                key
                for key in self._items
                if isinstance(key, AuthorizationCacheKey) and key.context == context
            ]
            for key in keys:
                del self._items[key]
            self._invalidations += len(keys)
            return len(keys)

    def stats(self) -> CacheStats:
        """Return current counters without exposing mutable storage."""

        with self._lock:
            return CacheStats(
                self._hits,
                self._misses,
                self._evictions,
                self._invalidations,
                len(self._items),
            )


@dataclass(frozen=True, slots=True)
class CachedEvaluation:
    """One post-match cache observation for the four-scheme experiment."""

    match: PolicyMatch
    cache_hit: bool
    key: AuthorizationCacheKey


def evaluate_baseline_cached(
    policy: CompiledPolicy,
    timestamp: int,
    context: AuthorizationCacheContext,
    cache: LruTtlCache[PolicyMatch],
) -> CachedEvaluation:
    """Evaluate Baseline-I and cache by its containing canonical interval."""

    match = BaselineIExecutor().evaluate(policy, timestamp)
    slot = _slot_at(policy, timestamp)
    if not match.allowed or slot is None:
        raise ValueError("cache experiments require an allowed request")
    interval = next(item for item in policy.intervals if item.contains(slot))
    key = AuthorizationCacheKey(
        context,
        "interval",
        interval.left,
        interval.length,
    )
    lookup = cache.lookup(key)
    if lookup.hit:
        assert lookup.value is not None
        return CachedEvaluation(lookup.value, True, key)
    cache.put(key, match)
    return CachedEvaluation(match, False, key)


def evaluate_proposed_cached(
    policy: CompiledPolicy,
    timestamp: int,
    context: AuthorizationCacheContext,
    cache: LruTtlCache[PolicyMatch],
) -> CachedEvaluation:
    """Evaluate Proposed-C and cache by its matched dyadic node."""

    match = ProposedCExecutor().evaluate(policy, timestamp)
    if not match.allowed or match.matched_node is None:
        raise ValueError("cache experiments require an allowed request")
    key = AuthorizationCacheKey(
        context,
        "node",
        match.matched_node.start,
        match.matched_node.size,
        match.cover_version,
    )
    lookup = cache.lookup(key)
    if lookup.hit:
        assert lookup.value is not None
        return CachedEvaluation(lookup.value, True, key)
    cache.put(key, match)
    return CachedEvaluation(match, False, key)
