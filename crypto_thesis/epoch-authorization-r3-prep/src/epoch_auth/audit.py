"""In-memory audit events for deterministic prototype inspection."""

from __future__ import annotations

from dataclasses import dataclass
from threading import RLock

from .errors import RejectCode


@dataclass(frozen=True, slots=True)
class AuditEvent:
    """One issuance or verification outcome without secret material."""

    action: str
    resource_id: str
    epoch: int | None
    accepted: bool
    code: RejectCode | None
    timestamp: int


class AuditLog:
    """Thread-safe append-only audit log for the local prototype."""

    def __init__(self) -> None:
        self._events: list[AuditEvent] = []
        self._lock = RLock()

    def append(self, event: AuditEvent) -> None:
        """Append an immutable audit event."""

        with self._lock:
            self._events.append(event)

    def events(self) -> tuple[AuditEvent, ...]:
        """Return a snapshot of all events."""

        with self._lock:
            return tuple(self._events)
