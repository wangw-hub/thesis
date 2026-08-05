from types import SimpleNamespace

import pytest

from epoch_auth_r3.revocation.agent import RevocationAgent
from epoch_auth_r3.revocation.events import EventClass, NormalizedAuthorizationEventV1, normalize_event
from epoch_auth_r3.revocation.guard import AccessMaterialReleaseGuard, ReleaseDecision
from epoch_auth_r3.revocation.policy import HeaderUpdateKind
from epoch_auth_r3.revocation.resolver import (
    AffectedResourceResolver, IncompleteResourceIndex, RecipientIndexEntry,
)
from scripts.r3_i9.run_p9a_development import build_current_header_anchor


def _event(name="EpochAdvanced", tx=b"t" * 32):
    return normalize_event(
        chain_id=2026073005, contract_address="0x" + "1" * 40,
        event_name=name, event_signature=b"s" * 32, transaction_hash=tx,
        log_index=0, block_number=21, block_hash=b"b" * 32,
        args={"resourceId": b"r" * 32, "newEpoch": 2},
    )


def test_real_event_scanner_dev():
    event = _event()
    assert event.chain_id == 2026073005 and event.block_number == 21


def test_normalized_authorization_event():
    event = _event()
    assert isinstance(event, NormalizedAuthorizationEventV1)
    assert event.event_class is EventClass.DIRECT_RESOURCE


def test_event_idempotency():
    event = _event()
    assert event.identity == _event().identity


def test_affected_resource_resolution():
    assert AffectedResourceResolver([], complete=True).resolve(_event()) == ((b"r" * 32).hex(),)


def test_revocation_agent_task_generation():
    agent = RevocationAgent(
        AffectedResourceResolver([], complete=True),
        lambda resource, block: {"resourceStatus": "ACTIVE", "epoch": 2, "stateVersion": 2},
    )
    plans = agent.plan(_event())
    assert len(plans) == 1 and plans[0].update_kind is HeaderUpdateKind.HEADER_ONLY


def test_revocation_agent_no_duplicate_jobs():
    plans = RevocationAgent(
        AffectedResourceResolver([], complete=True),
        lambda resource, block: {"resourceStatus": "ACTIVE", "epoch": 2, "stateVersion": 2},
    ).plan(_event())
    assert len({(p.event_identity, p.resource_id) for p in plans}) == len(plans)


def test_expected_update_kind_frozen():
    assert HeaderUpdateKind.HEADER_ONLY.value == "HEADER_ONLY"


def test_recipient_index_incomplete_fail_closed():
    user_event = SimpleNamespace(event_class=EventClass.USER_SCOPE, user_id="u")
    with pytest.raises(IncompleteResourceIndex):
        AffectedResourceResolver([RecipientIndexEntry("r", "u", "k", 1)], complete=False).resolve(user_event)


def test_revocation_agent_material_release_guard():
    state = SimpleNamespace(consistency_class=SimpleNamespace(value="AUTHORIZATION_AHEAD_OF_HEADER"))
    assert AccessMaterialReleaseGuard().evaluate(state, header_object_valid=True) is ReleaseDecision.HEADER_UPDATE_PENDING


def test_revocation_agent_final_composite_consistent():
    state = SimpleNamespace(consistency_class=SimpleNamespace(value="CONSISTENT"))
    assert AccessMaterialReleaseGuard().evaluate(state, header_object_valid=True) is ReleaseDecision.ALLOW


def test_revocation_anchor_uses_event_state_versions():
    anchor = build_current_header_anchor(
        b"r" * 32, b"p" * 32, b"o" * 32, b"h" * 32,
        b"n" * 32, b"x" * 32, b"b" * 32, epoch=2, state_version=2,
    )
    assert anchor[3:5] == (2, 2)
