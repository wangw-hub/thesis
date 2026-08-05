"""Force a live epoch transition between the issuer's two state reads."""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from eth_account import Account
from time_policy.compiler import compile_policy
from time_policy.models import Interval
from web3 import Web3

PROJECT_ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from epoch_auth.baseline_i import BaselineIExecutor
from epoch_auth.blockchain.besu_gateway import BesuStateGateway
from epoch_auth.errors import RejectCode
from epoch_auth.issuer import CapabilityIssuer
from epoch_auth.models import AuthorizationRequest, Operation
from epoch_auth.state_store import PolicyRepository

ROOT = Path(__file__).resolve().parents[2]
SECRET_ROOT = Path(r"D:\Research\crypto_thesis\secrets\formal-authorization-chain-2026072901")
CHAIN_ID = 2026072901


def main() -> None:
    binding = json.loads((ROOT / "evidence" / "f8" / "service-binding.json").read_text())
    deployment = json.loads((ROOT / "evidence" / "f7" / "deployment.json").read_text())
    artifact = json.loads((ROOT / "contracts" / "AuthorizationState.json").read_text())
    web3 = Web3(Web3.HTTPProvider("http://192.168.6.133:8645", request_kwargs={"timeout": 10}))
    address = Web3.to_checksum_address(deployment["contract_address"])
    contract = web3.eth.contract(address=address, abi=artifact["abi"])
    gateway = BesuStateGateway(web3, contract, sender=binding["resource_registration"]["receipt"]["from"], confirmations=0)
    authorizer_key = (SECRET_ROOT / "authorizer" / "key.hex").read_text().strip()
    authorizer = Account.from_key(authorizer_key)
    transition_receipt: dict | None = None

    class RacingStore:
        def get_authorization_state(self, resource_id: str, user_id: str):
            nonlocal transition_receipt
            snapshot = gateway.get_authorization_state(resource_id, user_id)
            if transition_receipt is None:
                function = contract.functions.advanceEpoch(
                    Web3.keccak(text=resource_id), Web3.keccak(text="issuer-race")
                )
                tx = function.build_transaction(
                    {
                        "from": authorizer.address,
                        "chainId": CHAIN_ID,
                        "nonce": web3.eth.get_transaction_count(authorizer.address, "pending"),
                        "gas": 300000,
                        "maxPriorityFeePerGas": 1,
                        "maxFeePerGas": int(web3.eth.get_block("latest")["baseFeePerGas"]) * 3 + 1,
                        "type": 2,
                    }
                )
                signed = Account.sign_transaction(tx, authorizer_key)
                tx_hash = web3.eth.send_raw_transaction(signed.raw_transaction)
                transition_receipt = dict(web3.eth.wait_for_transaction_receipt(tx_hash, timeout=60))
                if transition_receipt["status"] != 1:
                    raise RuntimeError("race transition failed")
            return snapshot

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
    issuer = CapabilityIssuer(
        issuer_id="Issuer-1", signing_key=issuer_key, state_store=RacingStore(),
        policies=policies, executor=BaselineIExecutor(), chain_id=CHAIN_ID,
        contract_address=bytes.fromhex(address[2:]),
    )
    now = int(datetime.now(tz=UTC).timestamp())
    decision = issuer.issue(
        AuthorizationRequest(
            binding["resource_id"], binding["user_id"], user_public, Operation.READ,
            now, 120, bytes.fromhex("55" * 16),
        )
    )
    if decision.accepted or decision.code is not RejectCode.SYSTEM_STATE_UNAVAILABLE:
        raise RuntimeError("state race produced an erroneously valid capability")
    result = {
        "accepted": decision.accepted,
        "rejection_code": decision.code.value,
        "transition_transaction": transition_receipt["transactionHash"].hex(),
        "transition_status": transition_receipt["status"],
        "state_race_erroneous_issue_count": 0,
    }
    (ROOT / "evidence" / "f9" / "state-race.json").write_text(
        json.dumps(result, indent=2) + "\n"
    )
    print(json.dumps(result))


if __name__ == "__main__":
    main()
