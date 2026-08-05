from __future__ import annotations

from dataclasses import dataclass

from .events import EventClass, NormalizedAuthorizationEventV1


class IncompleteResourceIndex(RuntimeError):
    pass


@dataclass(frozen=True)
class RecipientIndexEntry:
    resource_id: str
    user_id: str
    recipient_key_id: str
    user_version: int
    active: bool = True


class AffectedResourceResolver:
    def __init__(self, entries: list[RecipientIndexEntry], *, complete: bool):
        self._entries = tuple(entries)
        self.complete = complete

    def resolve(self, event: NormalizedAuthorizationEventV1) -> tuple[str, ...]:
        if event.event_class == EventClass.DIRECT_RESOURCE:
            if event.resource_id is None:
                raise ValueError("direct resource event lacks resourceId")
            return (event.resource_id,)
        if event.event_class == EventClass.AUDIT_ONLY:
            return ()
        if not self.complete:
            raise IncompleteResourceIndex("INCOMPLETE_RESOURCE_RECIPIENT_INDEX")
        resources = sorted({
            e.resource_id for e in self._entries
            if e.user_id == event.user_id and e.active
        })
        return tuple(resources)
