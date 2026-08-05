from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from time_policy.compiler import compile_policy
from time_policy.models import Interval

from epoch_auth.baseline_i import BaselineIExecutor
from epoch_auth.issuer import CapabilityIssuer
from epoch_auth.keys import generate_private_key, public_key_bytes, user_key_id
from epoch_auth.models import (
    AuthorizationRequest,
    Operation,
    ResourceState,
    ResourceStatus,
    UserState,
    UserStatus,
)
from epoch_auth.nonce_store import InMemoryNonceStore
from epoch_auth.proposed_c import ProposedCExecutor
from epoch_auth.state_store import InMemoryStateStore, PolicyRepository
from epoch_auth.verifier import CapabilityVerifier


@pytest.fixture
def protocol_context():
    origin = datetime(2026, 1, 1, tzinfo=UTC)
    policy = compile_policy(
        [Interval(0, 10), Interval(20, 30)],
        time_origin=origin,
        delta=timedelta(seconds=60),
        domain_size=64,
    )
    state = InMemoryStateStore()
    policies = PolicyRepository()
    policies.add(policy)
    user_private = generate_private_key()
    user_public = public_key_bytes(user_private.public_key())
    state.register_user(UserState("user-1", user_key_id(user_public), UserStatus.ACTIVE))
    state.register_resource(
        ResourceState(
            "resource-1",
            "owner-1",
            policy.digest,
            1,
            ResourceStatus.ACTIVE,
            1,
        )
    )
    issuer_key = generate_private_key()

    def build(executor):
        nonces = InMemoryNonceStore()
        issuer = CapabilityIssuer(
            issuer_id="as-1",
            signing_key=issuer_key,
            state_store=state,
            policies=policies,
            executor=executor,
        )
        verifier = CapabilityVerifier(
            issuer_public_key=issuer_key.public_key(),
            state_store=state,
            policies=policies,
            nonce_store=nonces,
            executor=executor,
        )
        return issuer, verifier, nonces

    now = int(origin.timestamp()) + 120
    request = AuthorizationRequest(
        "resource-1",
        "user-1",
        user_public,
        Operation.READ,
        now,
        300,
        b"\x11" * 16,
    )
    return {
        "origin": origin,
        "policy": policy,
        "state": state,
        "policies": policies,
        "issuer_key": issuer_key,
        "user_private": user_private,
        "user_public": user_public,
        "now": now,
        "request": request,
        "baseline": build(BaselineIExecutor()),
        "proposed": build(ProposedCExecutor()),
    }
