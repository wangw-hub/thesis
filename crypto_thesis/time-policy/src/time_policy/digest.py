"""SHA-256 digests for canonical time-policy representations."""

from __future__ import annotations

from hashlib import sha256
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import CompiledPolicy


def digest_bytes(canonical_bytes: bytes) -> bytes:
    """Return the 32-byte SHA-256 digest of canonical policy bytes."""

    return sha256(canonical_bytes).digest()


def policy_digest(compiled_policy: CompiledPolicy) -> bytes:
    """Recompute the policy digest from a compiled policy."""

    return digest_bytes(compiled_policy.canonical_bytes)
