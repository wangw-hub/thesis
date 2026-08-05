from datetime import UTC, datetime, timedelta

from time_policy.compiler import compile_policy
from time_policy.models import Interval

from epoch_auth.cache import (
    AuthorizationCacheContext,
    LruTtlCache,
    evaluate_baseline_cached,
)


def test_cache_hit_is_returned_by_each_lookup():
    policy = compile_policy(
        [Interval(0, 8)],
        time_origin=datetime(2026, 7, 29, tzinfo=UTC),
        delta=timedelta(minutes=1),
        domain_size=8,
    )
    context = AuthorizationCacheContext(1, b"x" * 20, "r", policy.digest, 1, 1,
                                        b"u" * 32, 1, 1)
    cache = LruTtlCache(4, 10**12)
    timestamp = int(policy.time_origin.timestamp())
    first = evaluate_baseline_cached(policy, timestamp, context, cache)
    second = evaluate_baseline_cached(policy, timestamp, context, cache)
    assert first.cache_hit is False
    assert second.cache_hit is True

