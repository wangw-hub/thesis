from __future__ import annotations

from dataclasses import replace

import pytest

from epoch_auth.errors import RejectCode
from epoch_auth.keys import generate_private_key, public_key_bytes, sign, user_key_id
from epoch_auth.models import (
    AuthorizationRequest,
    CapabilityPayload,
    Operation,
    ResourceStatus,
    SignedCapability,
)
from epoch_auth.serialization import encode_capability
from epoch_auth.token import parse_signed_capability


def verify(ctx, cap, **overrides):
    args = {
        "user_id": "user-1",
        "user_public_key": ctx["user_public"],
        "operation": Operation.READ,
        "now": ctx["now"],
    }
    args.update(overrides)
    return ctx["baseline"][1].verify(cap, **args)


def test_issuer_rejection_paths(protocol_context):
    ctx = protocol_context
    issuer = ctx["baseline"][0]
    unknown_resource = replace(ctx["request"], resource_id="missing")
    assert issuer.issue(unknown_resource).code is RejectCode.RESOURCE_NOT_FOUND
    unknown_user = replace(ctx["request"], user_id="missing")
    assert issuer.issue(unknown_user).code is RejectCode.USER_NOT_FOUND
    other_public = public_key_bytes(generate_private_key().public_key())
    wrong_key = replace(ctx["request"], user_public_key=other_public)
    assert issuer.issue(wrong_key).code is RejectCode.USER_KEY_MISMATCH
    ctx["state"].set_status("resource-1", ResourceStatus.SUSPENDED)
    assert issuer.issue(ctx["request"]).code is RejectCode.RESOURCE_INACTIVE
    assert len(issuer.audit_log.events()) == 4


def test_verifier_rejection_order_and_missing_state(protocol_context):
    ctx = protocol_context
    cap = ctx["baseline"][0].issue(ctx["request"]).capability
    assert verify(ctx, cap, user_id="missing").code is RejectCode.USER_NOT_FOUND
    altered = replace(cap.payload, resource_id="missing")
    raw = encode_capability(altered)
    missing_resource = SignedCapability(altered, raw, sign(ctx["issuer_key"], raw))
    assert verify(ctx, missing_resource).code is RejectCode.RESOURCE_NOT_FOUND
    ctx["state"].update_policy("resource-1", b"z" * 32)
    assert verify(ctx, cap).code is RejectCode.POLICY_DIGEST_MISMATCH


def test_malformed_exact_bytes_and_parse_helper(protocol_context):
    ctx = protocol_context
    cap = ctx["baseline"][0].issue(ctx["request"]).capability
    parsed = parse_signed_capability(cap.payload_bytes, cap.signature)
    assert parsed == cap
    malformed = SignedCapability(cap.payload, cap.payload_bytes + b"\x00", cap.signature)
    assert verify(ctx, malformed).code is RejectCode.MALFORMED_TOKEN


def test_proposed_node_binding_is_verified(protocol_context):
    ctx = protocol_context
    cap = ctx["proposed"][0].issue(ctx["request"]).capability
    altered = replace(cap.payload, cover_version=b"x" * 32)
    raw = encode_capability(altered)
    signed = SignedCapability(altered, raw, sign(ctx["issuer_key"], raw))
    result = ctx["proposed"][1].verify(
        signed,
        user_id="user-1",
        user_public_key=ctx["user_public"],
        operation=Operation.READ,
        now=ctx["now"],
    )
    assert result.code is RejectCode.TIME_POLICY_DENIED


@pytest.mark.parametrize(
    "factory",
    [
        lambda: CapabilityPayload(
            2, "i", "r", b"d" * 32, 1, b"k" * 32, Operation.READ, 1, 2, b"n" * 16, 1
        ),
        lambda: CapabilityPayload(
            1, "", "r", b"d" * 32, 1, b"k" * 32, Operation.READ, 1, 2, b"n" * 16, 1
        ),
        lambda: CapabilityPayload(
            1, "i", "r", b"d" * 31, 1, b"k" * 32, Operation.READ, 1, 2, b"n" * 16, 1
        ),
        lambda: CapabilityPayload(
            1, "i", "r", b"d" * 32, -1, b"k" * 32, Operation.READ, 1, 2, b"n" * 16, 1
        ),
        lambda: CapabilityPayload(
            1, "i", "r", b"d" * 32, 1, b"k" * 32, Operation.READ, 2, 2, b"n" * 16, 2
        ),
        lambda: CapabilityPayload(
            1, "i", "r", b"d" * 32, 1, b"k" * 32, Operation.READ, 1, 2, b"n" * 15, 1
        ),
    ],
)
def test_payload_validation(factory):
    with pytest.raises(ValueError):
        factory()


def test_key_fingerprint_rejects_wrong_length():
    with pytest.raises(ValueError):
        user_key_id(b"short")


def test_verifier_maps_malformed_public_key_to_rejection(protocol_context):
    ctx = protocol_context
    cap = ctx["baseline"][0].issue(ctx["request"]).capability
    assert verify(ctx, cap, user_public_key=b"short").code is RejectCode.USER_KEY_MISMATCH
