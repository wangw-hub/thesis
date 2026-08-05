"""Exercise CAP2 issuance, verification, and invalidation on the real Besu network."""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from time_policy.compiler import compile_policy
from time_policy.models import Interval
from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware

from epoch_auth.baseline_i import BaselineIExecutor
from epoch_auth.blockchain.besu_gateway import BesuStateGateway
from epoch_auth.errors import RejectCode
from epoch_auth.issuer import CapabilityIssuer
from epoch_auth.keys import public_key_bytes, user_key_id
from epoch_auth.models import (
    AuthorizationRequest,
    Operation,
    ResourceStatus,
    UserStatus,
)
from epoch_auth.nonce_store import InMemoryNonceStore
from epoch_auth.proposed_c import ProposedCExecutor
from epoch_auth.state_store import PolicyRepository
from epoch_auth.verifier import CapabilityVerifier

ROOT = Path(__file__).resolve().parents[1]
PRIVATE_KEY = "0x" + "00" * 31 + "01"


def main() -> None:
    """Run deterministic semantic checks and preserve their evidence as JSON."""

    deployment = json.loads(
        (ROOT / "blockchain" / "besu" / "deployment.json").read_text("utf-8")
    )
    artifact = json.loads(
        (ROOT / "contracts" / "build" / "AuthorizationState.json").read_text("utf-8")
    )
    w3 = Web3(Web3.HTTPProvider(deployment["rpc_url"]))
    w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
    contract = w3.eth.contract(
        address=deployment["contract_address"], abi=artifact["abi"]
    )
    gateway = BesuStateGateway(
        w3,
        contract,
        sender=deployment["deployer"],
        private_key=PRIVATE_KEY,
        receipt_timeout=60,
    )

    origin = datetime(2026, 7, 28, tzinfo=UTC)
    policy = compile_policy(
        [Interval(0, 1440)],
        time_origin=origin,
        delta=timedelta(minutes=1),
        domain_size=1440,
    )
    policies = PolicyRepository()
    policies.add(policy)
    policy_v2 = compile_policy(
        [Interval(0, 1439)],
        time_origin=origin,
        delta=timedelta(minutes=1),
        domain_size=1440,
    )
    policies.add(policy_v2)
    user_private = Ed25519PrivateKey.generate()
    user_public = public_key_bytes(user_private.public_key())
    gateway.register_user("besu-user-v1", deployment["deployer"], user_key_id(user_public))
    gateway.register_resource(
        "besu-resource-v1", deployment["deployer"], policy.digest
    )

    issuer_key = Ed25519PrivateKey.generate()
    address_bytes = bytes.fromhex(deployment["contract_address"][2:])
    issuer = CapabilityIssuer(
        issuer_id="besu-as-1",
        signing_key=issuer_key,
        state_store=gateway,
        policies=policies,
        executor=BaselineIExecutor(),
        chain_id=deployment["chain_id"],
        contract_address=address_bytes,
    )
    verifier = CapabilityVerifier(
        issuer_public_key=issuer_key.public_key(),
        state_store=gateway,
        policies=policies,
        nonce_store=InMemoryNonceStore(),
        executor=BaselineIExecutor(),
        chain_id=deployment["chain_id"],
        contract_address=address_bytes,
    )
    proposed_issuer = CapabilityIssuer(
        issuer_id="besu-as-1",
        signing_key=issuer_key,
        state_store=gateway,
        policies=policies,
        executor=ProposedCExecutor(),
        chain_id=deployment["chain_id"],
        contract_address=address_bytes,
    )
    proposed_verifier = CapabilityVerifier(
        issuer_public_key=issuer_key.public_key(),
        state_store=gateway,
        policies=policies,
        nonce_store=InMemoryNonceStore(),
        executor=ProposedCExecutor(),
        chain_id=deployment["chain_id"],
        contract_address=address_bytes,
    )
    now = int(origin.timestamp()) + 600

    def issue(nonce_byte: int, selected_issuer=issuer):
        request = AuthorizationRequest(
            "besu-resource-v1",
            "besu-user-v1",
            user_public,
            Operation.READ,
            now,
            300,
            bytes([nonce_byte]) * 16,
        )
        decision = selected_issuer.issue(request)
        if not decision.accepted:
            raise RuntimeError(f"issuance failed: {decision.code}")
        return decision.capability

    cap = issue(1)
    accepted = verifier.verify(
        cap,
        user_id="besu-user-v1",
        user_public_key=user_public,
        operation=Operation.READ,
        now=now,
    )
    replay = verifier.verify(
        cap,
        user_id="besu-user-v1",
        user_public_key=user_public,
        operation=Operation.READ,
        now=now,
    )
    proposed_cap = issue(4, proposed_issuer)
    proposed_accepted = proposed_verifier.verify(
        proposed_cap,
        user_id="besu-user-v1",
        user_public_key=user_public,
        operation=Operation.READ,
        now=now,
    )
    wrong_contract = CapabilityVerifier(
        issuer_public_key=issuer_key.public_key(),
        state_store=gateway,
        policies=policies,
        nonce_store=InMemoryNonceStore(),
        executor=ProposedCExecutor(),
        chain_id=deployment["chain_id"],
        contract_address=b"\x99" * 20,
    ).verify(
        proposed_cap,
        user_id="besu-user-v1",
        user_public_key=user_public,
        operation=Operation.READ,
        now=now,
    )
    stale_policy_cap = issue(5)
    gateway.update_policy("besu-resource-v1", policy_v2.digest)
    stale_policy = CapabilityVerifier(
        issuer_public_key=issuer_key.public_key(),
        state_store=gateway,
        policies=policies,
        nonce_store=InMemoryNonceStore(),
        executor=BaselineIExecutor(),
        chain_id=deployment["chain_id"],
        contract_address=address_bytes,
    ).verify(
        stale_policy_cap,
        user_id="besu-user-v1",
        user_public_key=user_public,
        operation=Operation.READ,
        now=now,
    )
    stale_epoch_cap = issue(2)
    gateway.advance_epoch("besu-resource-v1", Web3.keccak(text="semantic-check"))
    stale_epoch = verifier.verify(
        stale_epoch_cap,
        user_id="besu-user-v1",
        user_public_key=user_public,
        operation=Operation.READ,
        now=now,
    )
    rotation_cap = issue(3)
    gateway.rotate_user_key("besu-user-v1", b"\x66" * 32)
    stale_user = verifier.verify(
        rotation_cap,
        user_id="besu-user-v1",
        user_public_key=user_public,
        operation=Operation.READ,
        now=now,
    )
    wrong_chain = CapabilityVerifier(
        issuer_public_key=issuer_key.public_key(),
        state_store=gateway,
        policies=policies,
        nonce_store=InMemoryNonceStore(),
        executor=BaselineIExecutor(),
        chain_id=deployment["chain_id"] + 1,
        contract_address=address_bytes,
    ).verify(
        rotation_cap,
        user_id="besu-user-v1",
        user_public_key=user_public,
        operation=Operation.READ,
        now=now,
    )
    gateway.set_user_status("besu-user-v1", UserStatus.SUSPENDED)
    suspended_user = CapabilityVerifier(
        issuer_public_key=issuer_key.public_key(),
        state_store=gateway,
        policies=policies,
        nonce_store=InMemoryNonceStore(),
        executor=BaselineIExecutor(),
        chain_id=deployment["chain_id"],
        contract_address=address_bytes,
    ).verify(
        rotation_cap,
        user_id="besu-user-v1",
        user_public_key=user_public,
        operation=Operation.READ,
        now=now,
    )
    gateway.set_resource_status("besu-resource-v1", ResourceStatus.REVOKED)
    revoked_resource = CapabilityVerifier(
        issuer_public_key=issuer_key.public_key(),
        state_store=gateway,
        policies=policies,
        nonce_store=InMemoryNonceStore(),
        executor=BaselineIExecutor(),
        chain_id=deployment["chain_id"],
        contract_address=address_bytes,
    ).verify(
        rotation_cap,
        user_id="besu-user-v1",
        user_public_key=user_public,
        operation=Operation.READ,
        now=now,
    )
    report = {
        "chain_id": w3.eth.chain_id,
        "contract_address": deployment["contract_address"],
        "block_number": w3.eth.block_number,
        "peer_count": w3.net.peer_count,
        "cap2_accepted": accepted.accepted,
        "proposed_cap2_accepted": proposed_accepted.accepted,
        "replay_code": replay.code,
        "cross_contract_code": wrong_contract.code,
        "stale_policy_code": stale_policy.code,
        "stale_epoch_code": stale_epoch.code,
        "stale_user_code": stale_user.code,
        "cross_chain_code": wrong_chain.code,
        "suspended_user_code": suspended_user.code,
        "revoked_resource_code": revoked_resource.code,
        "expected": {
            "replay_code": RejectCode.NONCE_REPLAY,
            "cross_contract_code": RejectCode.CHAIN_CONTEXT_MISMATCH,
            "stale_policy_code": RejectCode.POLICY_DIGEST_MISMATCH,
            "stale_epoch_code": RejectCode.EPOCH_MISMATCH,
            "stale_user_code": RejectCode.USER_VERSION_MISMATCH,
            "cross_chain_code": RejectCode.CHAIN_CONTEXT_MISMATCH,
            "suspended_user_code": RejectCode.USER_INACTIVE,
            "revoked_resource_code": RejectCode.RESOURCE_INACTIVE,
        },
    }
    output = ROOT / "blockchain" / "besu" / "semantic-check.json"
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
