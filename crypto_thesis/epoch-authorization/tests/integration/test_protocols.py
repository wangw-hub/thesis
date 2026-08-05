from __future__ import annotations

from dataclasses import replace

from epoch_auth.errors import RejectCode
from epoch_auth.models import AuthorizationRequest, Operation


def test_both_protocols_issue_and_verify_same_semantics(protocol_context):
    ctx = protocol_context
    decisions = []
    for name in ("baseline", "proposed"):
        issuer, verifier, _ = ctx[name]
        issued = issuer.issue(ctx["request"])
        assert issued.accepted
        verified = verifier.verify(
            issued.capability,
            user_id="user-1",
            user_public_key=ctx["user_public"],
            operation=Operation.READ,
            now=ctx["now"],
        )
        decisions.append(verified.accepted)
    assert decisions == [True, True]


def test_proposed_really_binds_cover_node(protocol_context):
    issued = protocol_context["proposed"][0].issue(protocol_context["request"])
    assert issued.capability.payload.matched_node is not None
    assert issued.capability.payload.cover_version is not None
    baseline = protocol_context["baseline"][0].issue(protocol_context["request"])
    assert baseline.capability.payload.matched_node is None


def test_denied_slot_is_consistent(protocol_context):
    ctx = protocol_context
    denied = replace(ctx["request"], now=int(ctx["origin"].timestamp()) + 15 * 60)
    for name in ("baseline", "proposed"):
        result = ctx[name][0].issue(denied)
        assert not result.accepted
        assert result.code is RejectCode.TIME_POLICY_DENIED


def test_ttl_is_same_for_both_protocols(protocol_context):
    ctx = protocol_context
    expiries = [
        ctx[name][0].issue(ctx["request"]).capability.payload.expires_at
        for name in ("baseline", "proposed")
    ]
    assert expiries[0] == expiries[1]


def test_operation_binding(protocol_context):
    ctx = protocol_context
    issued = ctx["baseline"][0].issue(ctx["request"])
    result = ctx["baseline"][1].verify(
        issued.capability,
        user_id="user-1",
        user_public_key=ctx["user_public"],
        operation=Operation.UPDATE,
        now=ctx["now"],
    )
    assert result.code is RejectCode.OPERATION_MISMATCH
