from __future__ import annotations

from epoch_auth.baseline_i import BaselineIExecutor
from epoch_auth.errors import RejectCode
from epoch_auth.issuer import CapabilityIssuer
from epoch_auth.models import Operation, SignedCapability
from epoch_auth.nonce_store import InMemoryNonceStore
from epoch_auth.serialization import encode_capability
from epoch_auth.verifier import CapabilityVerifier


def build_cap2(ctx, chain_id=20260728, address=b"\x12" * 20):
    executor = BaselineIExecutor()
    issuer = CapabilityIssuer(
        issuer_id="as-1",
        signing_key=ctx["issuer_key"],
        state_store=ctx["state"],
        policies=ctx["policies"],
        executor=executor,
        chain_id=chain_id,
        contract_address=address,
    )
    verifier = CapabilityVerifier(
        issuer_public_key=ctx["issuer_key"].public_key(),
        state_store=ctx["state"],
        policies=ctx["policies"],
        nonce_store=InMemoryNonceStore(),
        executor=executor,
        chain_id=chain_id,
        contract_address=address,
    )
    return issuer, verifier


def verify(ctx, verifier, cap):
    return verifier.verify(
        cap,
        user_id="user-1",
        user_public_key=ctx["user_public"],
        operation=Operation.READ,
        now=ctx["now"],
    )


def test_cap2_binds_chain_contract_and_versions(protocol_context):
    ctx = protocol_context
    issuer, verifier = build_cap2(ctx)
    cap = issuer.issue(ctx["request"]).capability
    assert cap.payload.version == 2
    assert verify(ctx, verifier, cap).accepted


def test_cross_chain_and_contract_are_rejected(protocol_context):
    ctx = protocol_context
    issuer, _ = build_cap2(ctx)
    cap = issuer.issue(ctx["request"]).capability
    _, wrong_chain = build_cap2(ctx, chain_id=999)
    assert verify(ctx, wrong_chain, cap).code is RejectCode.CHAIN_CONTEXT_MISMATCH
    _, wrong_contract = build_cap2(ctx, address=b"\x34" * 20)
    assert verify(ctx, wrong_contract, cap).code is RejectCode.CHAIN_CONTEXT_MISMATCH


def test_user_version_change_rejects_old_cap2(protocol_context):
    ctx = protocol_context
    issuer, verifier = build_cap2(ctx)
    cap = issuer.issue(ctx["request"]).capability
    ctx["state"].rotate_user_key("user-1", b"\x44" * 32)
    assert verify(ctx, verifier, cap).code is RejectCode.USER_VERSION_MISMATCH


def test_cap1_rejected_by_chain_bound_verifier(protocol_context):
    ctx = protocol_context
    cap1 = ctx["baseline"][0].issue(ctx["request"]).capability
    _, verifier = build_cap2(ctx)
    assert verify(ctx, verifier, cap1).code is RejectCode.CHAIN_CONTEXT_MISMATCH
