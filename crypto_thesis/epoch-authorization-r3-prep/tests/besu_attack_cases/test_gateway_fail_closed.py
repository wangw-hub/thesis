from __future__ import annotations

from epoch_auth.blockchain.errors import GatewayUnavailable
from epoch_auth.errors import RejectCode


class UnavailableStore:
    def get_authorization_state(self, resource_id, user_id):
        raise GatewayUnavailable("injected outage")


class RacingStore:
    def __init__(self, stable_store):
        self.stable_store = stable_store
        self.calls = 0

    def get_authorization_state(self, resource_id, user_id):
        self.calls += 1
        resource, user = self.stable_store.get_authorization_state(resource_id, user_id)
        if self.calls == 2:
            return self.stable_store.advance_epoch(resource_id), user
        return resource, user


def test_issuer_fails_closed_when_gateway_is_unavailable(protocol_context):
    issuer = protocol_context["baseline"][0]
    issuer.state_store = UnavailableStore()
    decision = issuer.issue(protocol_context["request"])
    assert decision.code is RejectCode.SYSTEM_STATE_UNAVAILABLE


def test_issuer_fails_closed_on_state_race(protocol_context):
    issuer = protocol_context["baseline"][0]
    issuer.state_store = RacingStore(protocol_context["state"])
    decision = issuer.issue(protocol_context["request"])
    assert decision.code is RejectCode.SYSTEM_STATE_UNAVAILABLE


def test_verifier_fails_closed_when_gateway_is_unavailable(protocol_context):
    issuer, verifier, _ = protocol_context["baseline"]
    capability = issuer.issue(protocol_context["request"]).capability
    verifier.state_store = UnavailableStore()
    decision = verifier.verify(
        capability,
        user_id="user-1",
        user_public_key=protocol_context["user_public"],
        operation=protocol_context["request"].operation,
        now=protocol_context["now"],
    )
    assert decision.code is RejectCode.SYSTEM_STATE_UNAVAILABLE
