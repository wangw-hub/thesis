"""Bounded, fail-closed Research Content 3 revocation workflow."""

from .events import (
    AUTHORIZATION_EVENT_MANIFEST,
    EventClass,
    NormalizedAuthorizationEventV1,
    normalize_event,
)
from .policy import HeaderUpdateDecision, HeaderUpdateKind, decide_update
from .resolver import AffectedResourceResolver, IncompleteResourceIndex

__all__ = [
    "AUTHORIZATION_EVENT_MANIFEST",
    "AffectedResourceResolver",
    "EventClass",
    "HeaderUpdateDecision",
    "HeaderUpdateKind",
    "IncompleteResourceIndex",
    "NormalizedAuthorizationEventV1",
    "decide_update",
    "normalize_event",
]
