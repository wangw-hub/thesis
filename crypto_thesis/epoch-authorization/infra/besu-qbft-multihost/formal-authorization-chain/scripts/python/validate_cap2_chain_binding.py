"""Validate CAP2 issuance and verification against the live formal Besu state."""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from time_policy.compiler import compile_policy
from time_policy.models import Interval
from web3 import Web3

from epoch_auth.baseline_i import BaselineIExecutor
from epoch_auth.blockchain.besu_gateway import BesuStateGateway
from epoch_auth.issuer import CapabilityIssuer
from epoch_auth.models import AuthorizationRequest, Operation
from epoch_auth.nonce_store import InMemoryNonceStore
from epoch_auth.proposed_c import ProposedCExecutor
from epoch_auth.state_store import PolicyRepository
from epoch_auth.verifier import CapabilityVerifier

ROOT = Path(__file__).resolve().parents[2]
SECRET_ROOT = Path(r"D:\Research\crypto_thesis\secrets\formal-authorization-chain-2026072901")
RPC_URL = "http://192.168.6.133:8645"
CHAIN_ID = 2026072901


def main() -> None:
    binding = json.loads((ROOT / "evidence" / "f8" / "service-binding.json").read_text())
    deployment = json.loads((ROOT / "evidence" / "f7" / "deployment.json").read_text())
    artifact = json.loads((ROOT / "contracts" / "AuthorizationState.json").read_text())
    web3 = Web3(Web3.HTTPProvider(RPC_URL, request_kwargs={"timeout": 10}))
    if not web3.is_connected() or web3.eth.chain_id != CHAIN_ID:
        raise RuntimeError("formal RPC or chain binding unavailable")
    contract_address = Web3.to_checksum_address(deployment["contract_address"])
    contract = web3.eth.contract(address=contract_address, abi=artifact["abi"])
    gateway = BesuStateGateway(
        web3,
        contract,
        sender=binding["resource_registration"]["receipt"]["from"],
        confirmations=1,
    )
    policy = compile_policy(
        [Interval(0, 1440)],
        time_origin=datetime(2026, 7, 29, tzinfo=UTC),
        delta=timedelta(minutes=1),
        domain_size=1440,
    )
    if policy.digest.hex() != binding["policy_digest"]:
        raise RuntimeError("policy digest does not match live resource")
    policies = PolicyRepository()
    policies.add(policy)
    issuer_key = Ed25519PrivateKey.from_private_bytes(
        (SECRET_ROOT / "services" / "issuer-1" / "ed25519-private.raw").read_bytes()
    )
    user_public = (SECRET_ROOT / "services" / "user-1" / "ed25519-public.raw").read_bytes()
    now = int(datetime.now(tz=UTC).timestamp())
    results = {}
    for name, executor in (
        ("B0", BaselineIExecutor()),
        ("C0", ProposedCExecutor()),
    ):
        issuer = CapabilityIssuer(
            issuer_id="Issuer-1",
            signing_key=issuer_key,
            state_store=gateway,
            policies=policies,
            executor=executor,
            chain_id=CHAIN_ID,
            contract_address=bytes.fromhex(contract_address[2:]),
        )
        verifier = CapabilityVerifier(
            issuer_public_key=issuer_key.public_key(),
            state_store=gateway,
            policies=policies,
            nonce_store=InMemoryNonceStore(),
            executor=executor,
            chain_id=CHAIN_ID,
            contract_address=bytes.fromhex(contract_address[2:]),
        )
        request = AuthorizationRequest(
            binding["resource_id"],
            binding["user_id"],
            user_public,
            Operation.READ,
            now,
            120,
            bytes.fromhex("10" if name == "B0" else "20") * 16,
        )
        issued = issuer.issue(request)
        if not issued.accepted or issued.capability is None:
            raise RuntimeError(f"{name} issuance rejected: {issued.code}")
        verified = verifier.verify(
            issued.capability,
            user_id=binding["user_id"],
            user_public_key=user_public,
            operation=Operation.READ,
            now=now,
        )
        payload = issued.capability.payload
        results[name] = {
            "issued": issued.accepted,
            "verified": verified.accepted,
            "version": payload.version,
            "chain_id": payload.chain_binding.chain_id,
            "contract_address": payload.chain_binding.contract_address.hex(),
            "resource_state_version": payload.chain_binding.resource_state_version,
            "user_version": payload.chain_binding.user_version,
            "has_cover_binding": payload.matched_node is not None,
        }
        if not verified.accepted or payload.version != 2:
            raise RuntimeError(f"{name} CAP2 verification failed")
    (ROOT / "evidence" / "f8" / "cap2-live-binding.json").write_text(
        json.dumps(results, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(results))


if __name__ == "__main__":
    main()
