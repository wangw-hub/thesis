"""Baseline-I policy execution over canonical intervals."""

from __future__ import annotations

from bisect import bisect_right
from dataclasses import dataclass
from datetime import UTC, datetime

from time_policy.matcher import interval_matcher
from time_policy.models import CompiledPolicy

from .models import MatchedNode


@dataclass(frozen=True, slots=True)
class PolicyMatch:
    """Result shared by both policy execution strategies."""

    allowed: bool
    window_end: int | None
    matched_node: MatchedNode | None = None
    cover_version: bytes | None = None


def _slot_at(policy: CompiledPolicy, timestamp: int) -> int | None:
    now = datetime.fromtimestamp(timestamp, tz=UTC)
    elapsed = now - policy.time_origin
    slot = int(elapsed // policy.delta)
    return slot if 0 <= slot < policy.domain_size else None


def _slot_end_timestamp(policy: CompiledPolicy, end_slot: int) -> int:
    return int((policy.time_origin + end_slot * policy.delta).timestamp())


def _containing_interval_end(policy: CompiledPolicy, slot: int) -> int:
    """Find the containing canonical interval end by binary search."""

    starts = tuple(item.left for item in policy.intervals)
    index = bisect_right(starts, slot) - 1
    if index < 0 or not policy.intervals[index].contains(slot):
        raise ValueError("allowed slot has no containing canonical interval")
    return policy.intervals[index].right


class BaselineIExecutor:
    """Strong baseline using binary search over the canonical interval list."""

    name = "Baseline-I"

    def evaluate(self, policy: CompiledPolicy, timestamp: int) -> PolicyMatch:
        """Evaluate time membership and return the containing window end."""

        slot = _slot_at(policy, timestamp)
        if slot is None:
            return PolicyMatch(False, None)
        matcher = interval_matcher(policy.intervals, policy.domain_size)
        if not matcher.match(slot):
            return PolicyMatch(False, None)
        end = _containing_interval_end(policy, slot)
        return PolicyMatch(True, _slot_end_timestamp(policy, end))

    def validate_binding(
        self, policy: CompiledPolicy, timestamp: int, node: MatchedNode | None, version: bytes | None
    ) -> bool:
        """Require baseline capabilities to omit hierarchical extensions."""

        return node is None and version is None and self.evaluate(policy, timestamp).allowed
