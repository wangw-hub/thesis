from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace

import pytest

from epoch_auth.errors import RejectCode
from epoch_auth.keys import generate_private_key, public_key_bytes, sign
from epoch_auth.models import Operation, ResourceStatus, SignedCapability, UserStatus
from epoch_auth.serialization import encode_capability


def resign(ctx, cap, **changes):
    payload = replace(cap.payload, **changes)
    raw = encode_capability(payload)
    return SignedCapability(payload, raw, sign(ctx["issuer_key"], raw))


@pytest.mark.attack
@pytest.mark.parametrize("protocol", ["baseline", "proposed"])
@pytest.mark.parametrize(
    "field,value",
    [
        ("resource_id", "resource-x"),
        ("policy_digest", b"x" * 32),
        ("epoch", 99),
        ("user_key_id", b"x" * 32),
        ("operation", Operation.UPDATE),
        ("not_before", 1),
        ("expires_at", (1 << 32)),
        ("nonce", b"x" * 16),
    ],
)
def test_unsigned_field_tampering_breaks_signature(protocol_context, protocol, field, value):
    ctx = protocol_context
    issued = ctx[protocol][0].issue(ctx["request"]).capability
    altered = replace(issued.payload, **{field: value})
    tampered = SignedCapability(altered, encode_capability(altered), issued.signature)
    result = ctx[protocol][1].verify(
        tampered,
        user_id="user-1",
        user_public_key=ctx["user_public"],
        operation=altered.operation,
        now=max(ctx["now"], altered.not_before),
    )
    assert result.code is RejectCode.INVALID_SIGNATURE


@pytest.mark.attack
@pytest.mark.parametrize("protocol", ["baseline", "proposed"])
def test_forged_signature(protocol_context, protocol):
    ctx = protocol_context
    cap = ctx[protocol][0].issue(ctx["request"]).capability
    forged = SignedCapability(cap.payload, cap.payload_bytes, b"\x00" * 64)
    result = ctx[protocol][1].verify(
        forged,
        user_id="user-1",
        user_public_key=ctx["user_public"],
        operation=Operation.READ,
        now=ctx["now"],
    )
    assert result.code is RejectCode.INVALID_SIGNATURE


@pytest.mark.attack
@pytest.mark.parametrize("protocol", ["baseline", "proposed"])
def test_old_epoch_token(protocol_context, protocol):
    ctx = protocol_context
    cap = ctx[protocol][0].issue(ctx["request"]).capability
    ctx["state"].advance_epoch("resource-1")
    result = ctx[protocol][1].verify(
        cap,
        user_id="user-1",
        user_public_key=ctx["user_public"],
        operation=Operation.READ,
        now=ctx["now"],
    )
    assert result.code is RejectCode.EPOCH_MISMATCH


@pytest.mark.attack
@pytest.mark.parametrize("protocol", ["baseline", "proposed"])
def test_expired_and_not_yet_valid(protocol_context, protocol):
    ctx = protocol_context
    cap = ctx[protocol][0].issue(ctx["request"]).capability
    expired = ctx[protocol][1].verify(
        cap,
        user_id="user-1",
        user_public_key=ctx["user_public"],
        operation=Operation.READ,
        now=cap.payload.expires_at,
    )
    assert expired.code is RejectCode.EXPIRED
    future = resign(
        ctx,
        cap,
        not_before=ctx["now"] + 10,
        issued_at=ctx["now"] + 10,
        expires_at=ctx["now"] + 20,
    )
    early = ctx[protocol][1].verify(
        future,
        user_id="user-1",
        user_public_key=ctx["user_public"],
        operation=Operation.READ,
        now=ctx["now"],
    )
    assert early.code is RejectCode.NOT_YET_VALID


@pytest.mark.attack
@pytest.mark.parametrize("protocol", ["baseline", "proposed"])
def test_wrong_public_key(protocol_context, protocol):
    ctx = protocol_context
    cap = ctx[protocol][0].issue(ctx["request"]).capability
    other = public_key_bytes(generate_private_key().public_key())
    result = ctx[protocol][1].verify(
        cap,
        user_id="user-1",
        user_public_key=other,
        operation=Operation.READ,
        now=ctx["now"],
    )
    assert result.code is RejectCode.USER_KEY_MISMATCH


@pytest.mark.attack
@pytest.mark.parametrize("protocol", ["baseline", "proposed"])
def test_resource_and_user_inactive(protocol_context, protocol):
    ctx = protocol_context
    cap = ctx[protocol][0].issue(ctx["request"]).capability
    ctx["state"].set_status("resource-1", ResourceStatus.SUSPENDED)
    result = ctx[protocol][1].verify(
        cap,
        user_id="user-1",
        user_public_key=ctx["user_public"],
        operation=Operation.READ,
        now=ctx["now"],
    )
    assert result.code is RejectCode.RESOURCE_INACTIVE


@pytest.mark.attack
@pytest.mark.parametrize("protocol", ["baseline", "proposed"])
def test_user_inactive(protocol_context, protocol):
    ctx = protocol_context
    cap = ctx[protocol][0].issue(ctx["request"]).capability
    ctx["state"].set_user_status("user-1", UserStatus.SUSPENDED)
    result = ctx[protocol][1].verify(
        cap,
        user_id="user-1",
        user_public_key=ctx["user_public"],
        operation=Operation.READ,
        now=ctx["now"],
    )
    assert result.code is RejectCode.USER_INACTIVE


@pytest.mark.attack
@pytest.mark.parametrize("protocol", ["baseline", "proposed"])
def test_replay_and_concurrent_replay(protocol_context, protocol):
    ctx = protocol_context
    issuer, verifier, _ = ctx[protocol]
    cap = issuer.issue(ctx["request"]).capability

    def attempt(_):
        return verifier.verify(
            cap,
            user_id="user-1",
            user_public_key=ctx["user_public"],
            operation=Operation.READ,
            now=ctx["now"],
        )

    with ThreadPoolExecutor(max_workers=16) as pool:
        results = list(pool.map(attempt, range(50)))
    assert sum(item.accepted for item in results) == 1
    assert sum(item.code is RejectCode.NONCE_REPLAY for item in results) == 49
