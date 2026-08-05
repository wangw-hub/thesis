"""Live-chain semantic, CAP2 attack, cache, and state-race validation."""

from __future__ import annotations

import json
import random
import sys
from dataclasses import asdict, replace
from datetime import UTC, datetime, timedelta
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from time_policy.compiler import compile_policy
from time_policy.models import Interval
from web3 import Web3

PROJECT_ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from epoch_auth.baseline_i import BaselineIExecutor
from epoch_auth.blockchain.besu_gateway import BesuStateGateway
from epoch_auth.cache import (
    AuthorizationCacheContext,
    LruTtlCache,
    evaluate_baseline_cached,
    evaluate_proposed_cached,
)
from epoch_auth.errors import RejectCode
from epoch_auth.issuer import CapabilityIssuer
from epoch_auth.keys import sign
from epoch_auth.models import AuthorizationRequest, Operation, SignedCapability
from epoch_auth.nonce_store import InMemoryNonceStore
from epoch_auth.proposed_c import ProposedCExecutor
from epoch_auth.serialization import encode_capability
from epoch_auth.state_store import PolicyRepository
from epoch_auth.verifier import CapabilityVerifier

ROOT = Path(__file__).resolve().parents[2]
SECRET_ROOT = Path(r"D:\Research\crypto_thesis\secrets\formal-authorization-chain-2026072901")
CHAIN_ID = 2026072901
RPC_URL = "http://192.168.6.133:8645"


def main() -> None:
    binding = json.loads((ROOT / "evidence" / "f8" / "service-binding.json").read_text())
    deployment = json.loads((ROOT / "evidence" / "f7" / "deployment.json").read_text())
    artifact = json.loads((ROOT / "contracts" / "AuthorizationState.json").read_text())
    address = Web3.to_checksum_address(deployment["contract_address"])
    web3 = Web3(Web3.HTTPProvider(RPC_URL, request_kwargs={"timeout": 10}))
    contract = web3.eth.contract(address=address, abi=artifact["abi"])
    gateway = BesuStateGateway(web3, contract, sender=binding["resource_registration"]["receipt"]["from"], confirmations=1)
    policy = compile_policy(
        [Interval(0, 1440)],
        time_origin=datetime(2026, 7, 29, tzinfo=UTC),
        delta=timedelta(minutes=1),
        domain_size=1440,
    )
    policies = PolicyRepository()
    policies.add(policy)
    issuer_key = Ed25519PrivateKey.from_private_bytes(
        (SECRET_ROOT / "services" / "issuer-1" / "ed25519-private.raw").read_bytes()
    )
    user_public = (SECRET_ROOT / "services" / "user-1" / "ed25519-public.raw").read_bytes()
    resource, user = gateway.get_authorization_state(binding["resource_id"], binding["user_id"])
    context = AuthorizationCacheContext(
        CHAIN_ID, bytes.fromhex(address[2:]), binding["resource_id"], policy.digest,
        resource.epoch, resource.updated_version, user.user_key_id, user.user_version, int(Operation.READ),
    )
    baseline_cache = LruTtlCache(128, 60_000_000_000)
    proposed_cache = LruTtlCache(128, 60_000_000_000)
    rng = random.Random(2026072901)
    semantic_differences = 0
    for _ in range(1000):
        timestamp = int(policy.time_origin.timestamp()) + rng.randrange(0, 1440) * 60
        b0 = BaselineIExecutor().evaluate(policy, timestamp)
        c0 = ProposedCExecutor().evaluate(policy, timestamp)
        b1 = evaluate_baseline_cached(policy, timestamp, context, baseline_cache).match
        c1 = evaluate_proposed_cached(policy, timestamp, context, proposed_cache).match
        if len({b0.allowed, b1.allowed, c0.allowed, c1.allowed}) != 1:
            semantic_differences += 1

    now = int(datetime.now(tz=UTC).timestamp())
    request = AuthorizationRequest(
        binding["resource_id"], binding["user_id"], user_public, Operation.READ,
        now, 120, bytes.fromhex("31" * 16),
    )
    issuer = CapabilityIssuer(
        issuer_id="Issuer-1", signing_key=issuer_key, state_store=gateway,
        policies=policies, executor=BaselineIExecutor(), chain_id=CHAIN_ID,
        contract_address=bytes.fromhex(address[2:]),
    )
    issued = issuer.issue(request)
    if not issued.accepted or issued.capability is None:
        raise RuntimeError(f"live issuance failed: {issued.code}")
    cap = issued.capability

    def verifier(chain_id: int = CHAIN_ID, contract_address: bytes = bytes.fromhex(address[2:])):
        return CapabilityVerifier(
            issuer_public_key=issuer_key.public_key(), state_store=gateway,
            policies=policies, nonce_store=InMemoryNonceStore(),
            executor=BaselineIExecutor(), chain_id=chain_id,
            contract_address=contract_address,
        )

    def check(name: str, capability: SignedCapability, expected: RejectCode | None, **kwargs) -> None:
        decision = verifier(**kwargs).verify(
            capability, user_id=binding["user_id"], user_public_key=user_public,
            operation=Operation.READ, now=now,
        )
        actual = decision.code
        attacks.append({"attack": name, "accepted": decision.accepted, "code": actual.value if actual else None})
        if actual is not expected:
            raise RuntimeError(f"{name}: expected {expected}, got {actual}")

    attacks: list[dict] = []
    forged = SignedCapability(cap.payload, cap.payload_bytes, b"\x00" * 64)
    check("wrong_signature", forged, RejectCode.INVALID_SIGNATURE)
    check("cross_chain", cap, RejectCode.CHAIN_CONTEXT_MISMATCH, chain_id=CHAIN_ID + 1)
    check("cross_contract", cap, RejectCode.CHAIN_CONTEXT_MISMATCH, contract_address=b"\x44" * 20)
    operation_result = verifier().verify(
        cap, user_id=binding["user_id"], user_public_key=user_public,
        operation=Operation.UPDATE, now=now,
    )
    attacks.append({"attack": "operation_substitution", "accepted": operation_result.accepted, "code": operation_result.code.value})
    if operation_result.code is not RejectCode.OPERATION_MISMATCH:
        raise RuntimeError("operation substitution accepted")
    expired_result = verifier().verify(
        cap, user_id=binding["user_id"], user_public_key=user_public,
        operation=Operation.READ, now=cap.payload.expires_at,
    )
    attacks.append({"attack": "expired", "accepted": expired_result.accepted, "code": expired_result.code.value})
    future_payload = replace(cap.payload, not_before=now + 30, issued_at=now + 30, expires_at=now + 60)
    future_raw = encode_capability(future_payload)
    future = SignedCapability(future_payload, future_raw, sign(issuer_key, future_raw))
    future_result = verifier().verify(
        future, user_id=binding["user_id"], user_public_key=user_public,
        operation=Operation.READ, now=now,
    )
    attacks.append({"attack": "not_yet_valid", "accepted": future_result.accepted, "code": future_result.code.value})
    replay_verifier = verifier()
    first = replay_verifier.verify(cap, user_id=binding["user_id"], user_public_key=user_public, operation=Operation.READ, now=now)
    second = replay_verifier.verify(cap, user_id=binding["user_id"], user_public_key=user_public, operation=Operation.READ, now=now)
    attacks.append({"attack": "serial_replay", "first_accepted": first.accepted, "second_code": second.code.value})
    error_accepts = sum(1 for item in attacks if item.get("accepted") is True)
    if semantic_differences or error_accepts:
        raise RuntimeError("semantic or security acceptance failure")
    result = {
        "random_requests": 1000,
        "semantic_differences": semantic_differences,
        "attack_cases": attacks,
        "attack_error_accepts": error_accepts,
        "baseline_cache": asdict(baseline_cache.stats()),
        "proposed_cache": asdict(proposed_cache.stats()),
    }
    target = ROOT / "evidence" / "f9"
    target.mkdir(parents=True, exist_ok=True)
    (target / "live-security-and-semantics.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"random_requests": 1000, "semantic_differences": 0, "attack_error_accepts": 0}))


if __name__ == "__main__":
    main()
