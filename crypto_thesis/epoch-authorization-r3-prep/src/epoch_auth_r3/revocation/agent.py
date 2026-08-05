from __future__ import annotations

from dataclasses import dataclass

from .events import NormalizedAuthorizationEventV1
from .policy import HeaderUpdateKind, decide_update
from .resolver import AffectedResourceResolver


@dataclass(frozen=True)
class PlannedResourceUpdate:
    event_identity: tuple[int, str, str, int]
    resource_id: str
    update_kind: HeaderUpdateKind
    target_epoch: int
    target_state_version: int


class RevocationAgent:
    """Deterministic planning core; chain and database effects stay in adapters."""

    def __init__(self, resolver: AffectedResourceResolver, state_reader):
        self.resolver = resolver
        self.state_reader = state_reader

    def plan(self, event: NormalizedAuthorizationEventV1) -> tuple[PlannedResourceUpdate, ...]:
        plans = []
        for resource_id in self.resolver.resolve(event):
            state = self.state_reader(resource_id, event.block_number)
            decision = decide_update(
                event.event_name, resource_status=state["resourceStatus"]
            )
            if decision.kind == HeaderUpdateKind.POLICY_DECISION_REQUIRED:
                raise RuntimeError("POLICY_DECISION_REQUIRED")
            plans.append(PlannedResourceUpdate(
                event.identity,
                resource_id,
                decision.kind,
                int(state["epoch"]),
                int(state["stateVersion"]),
            ))
        return tuple(plans)
