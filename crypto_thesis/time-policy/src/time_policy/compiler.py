"""High-level orchestration for deterministic policy compilation."""

from __future__ import annotations

from collections.abc import Iterable
from datetime import UTC, datetime, timedelta

from .cover import cover_policy
from .digest import digest_bytes
from .errors import TimezoneRequiredError
from .models import CompiledPolicy, Interval
from .normalize import normalize
from .serialize import canonical_serialize


def compile_policy(
    intervals: Iterable[Interval],
    *,
    time_origin: datetime,
    delta: timedelta,
    domain_size: int,
) -> CompiledPolicy:
    """Compile raw integer intervals into all canonical representations."""

    if time_origin.tzinfo is None or time_origin.utcoffset() is None:
        raise TimezoneRequiredError("time_origin must be timezone-aware")
    origin_utc = time_origin.astimezone(UTC)
    normalized = normalize(intervals, domain_size=domain_size)
    cover = cover_policy(normalized, domain_size)
    canonical_bytes = canonical_serialize(
        time_origin=origin_utc,
        delta=delta,
        domain_size=domain_size,
        intervals=normalized,
    )
    digest = digest_bytes(canonical_bytes)
    return CompiledPolicy(
        time_origin=origin_utc,
        delta=delta,
        domain_size=domain_size,
        intervals=normalized,
        cover=cover,
        canonical_bytes=canonical_bytes,
        digest=digest,
    )
