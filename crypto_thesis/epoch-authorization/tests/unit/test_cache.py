from __future__ import annotations

from datetime import UTC, datetime, timedelta

from time_policy.compiler import compile_policy
from time_policy.models import Interval

from epoch_auth.cache import (
    AuthorizationCacheContext,
    LruTtlCache,
    evaluate_baseline_cached,
    evaluate_proposed_cached,
)


def policy_and_context():
    policy = compile_policy(
        [Interval(0, 16)],
        time_origin=datetime(2026, 1, 1, tzinfo=UTC),
        delta=timedelta(seconds=1),
        domain_size=32,
    )
    context = AuthorizationCacheContext(
        1, b"\x11" * 20, "r", policy.digest, 1, 1, b"\x22" * 32, 1, 1
    )
    return policy, context


def test_interval_cache_reuses_at_least_the_node_cache_scope():
    policy, context = policy_and_context()
    baseline = LruTtlCache(8, 1_000_000_000)
    proposed = LruTtlCache(8, 1_000_000_000)
    origin = int(policy.time_origin.timestamp())

    b1 = evaluate_baseline_cached(policy, origin + 1, context, baseline)
    b2 = evaluate_baseline_cached(policy, origin + 14, context, baseline)
    c1 = evaluate_proposed_cached(policy, origin + 1, context, proposed)
    c2 = evaluate_proposed_cached(policy, origin + 14, context, proposed)

    assert not b1.cache_hit and b2.cache_hit
    assert not c1.cache_hit and c2.cache_hit
    assert b1.key.segment_size >= c1.key.segment_size


def test_common_lru_ttl_and_context_invalidation():
    now = [0]
    cache = LruTtlCache(1, 10, clock=lambda: now[0])
    policy, context = policy_and_context()
    origin = int(policy.time_origin.timestamp())
    first = evaluate_baseline_cached(policy, origin + 1, context, cache)
    assert cache.invalidate_context(context) == 1
    evaluate_baseline_cached(policy, origin + 1, context, cache)
    now[0] = 11
    assert cache.get(first.key) is None
    stats = cache.stats()
    assert stats.invalidations == 2
    assert stats.misses >= 2
