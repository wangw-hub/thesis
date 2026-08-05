"""Proposed-C execution that actually consumes the dyadic cover."""

from __future__ import annotations

from hashlib import sha256

from time_policy.models import CompiledPolicy

from .baseline_i import (
    PolicyMatch,
    _containing_interval_end,
    _slot_at,
    _slot_end_timestamp,
)
from .models import MatchedNode


def cover_version(policy: CompiledPolicy) -> bytes:
    """Hash a deterministic fixed-width encoding of the derived cover."""

    encoded = b"CVR1" + b"".join(
        node.start.to_bytes(8, "big") + node.size.to_bytes(8, "big")
        for node in policy.cover
    )
    return sha256(encoded).digest()


class ProposedCExecutor:
    """Candidate executor using leaf-to-root node matching over ``C(P)``."""

    name = "Proposed-C"

    def evaluate(self, policy: CompiledPolicy, timestamp: int) -> PolicyMatch:
        """Match the current slot against a node in the derived cover."""

        slot = _slot_at(policy, timestamp)
        if slot is None:
            return PolicyMatch(False, None)
        nodes = {(node.start, node.size) for node in policy.cover}
        capacity = 1 << (policy.domain_size - 1).bit_length()
        size = 1
        while size <= capacity:
            start = slot & ~(size - 1)
            if (start, size) in nodes:
                node = MatchedNode(start, size)
                # CAP1 lifetime follows the same maximal semantic interval as
                # Baseline-I; C(P) is consumed only for the authorization match.
                interval_end = _containing_interval_end(policy, slot)
                return PolicyMatch(
                    True,
                    _slot_end_timestamp(policy, interval_end),
                    node,
                    cover_version(policy),
                )
            size <<= 1
        return PolicyMatch(False, None)

    def validate_binding(
        self, policy: CompiledPolicy, timestamp: int, node: MatchedNode | None, version: bytes | None
    ) -> bool:
        """Recompute and verify the node-level CAP1 binding."""

        actual = self.evaluate(policy, timestamp)
        return (
            actual.allowed
            and actual.matched_node == node
            and actual.cover_version == version
        )
