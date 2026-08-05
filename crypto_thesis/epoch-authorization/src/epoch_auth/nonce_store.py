"""Atomic one-time nonce consumption."""

from __future__ import annotations

from threading import RLock
from typing import Protocol


class NonceStore(Protocol):
    """One-time consumption interface."""

    def consume_once(self, resource_id: str, epoch: int, nonce: bytes) -> bool: ...


class InMemoryNonceStore:
    """Thread-safe nonce store used only by the local prototype."""

    def __init__(self) -> None:
        self._consumed: set[tuple[str, int, bytes]] = set()
        self._lock = RLock()

    def consume_once(self, resource_id: str, epoch: int, nonce: bytes) -> bool:
        """Atomically consume a nonce for one resource and Epoch."""

        key = (resource_id, epoch, nonce)
        with self._lock:
            if key in self._consumed:
                return False
            self._consumed.add(key)
            return True

    def count(self) -> int:
        """Return the number of consumed nonce tuples."""

        with self._lock:
            return len(self._consumed)
