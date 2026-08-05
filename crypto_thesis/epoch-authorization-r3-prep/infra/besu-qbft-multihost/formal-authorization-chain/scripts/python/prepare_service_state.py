"""Create external service keys and register active CAP2 test state."""

from __future__ import annotations

import json
import hashlib
import sys
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from eth_account import Account
from time_policy.compiler import compile_policy
from time_policy.models import Interval
from web3 import Web3

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fund_roles as transport

ROOT = Path(__file__).resolve().parents[2]
SECRET_ROOT = Path(r"D:\Research\crypto_thesis\secrets\formal-authorization-chain-2026072901")
CHAIN_ID = 2026072901


def ensure_ed25519(name: str) -> tuple[bytes, bytes]:
    directory = SECRET_ROOT / "services" / name
    directory.mkdir(parents=True, exist_ok=True)
    private_path = directory / "ed25519-private.raw"
    public_path = directory / "ed25519-public.raw"
    if not private_path.exists():
        private = Ed25519PrivateKey.generate()
        private_path.write_bytes(
            private.private_bytes(
                serialization.Encoding.Raw,
                serialization.PrivateFormat.Raw,
                serialization.NoEncryption(),
            )
        )
        public_path.write_bytes(
            private.public_key().public_bytes(
                serialization.Encoding.Raw, serialization.PublicFormat.Raw
            )
        )
    private_raw = private_path.read_bytes()
    public_raw = public_path.read_bytes()
    if len(private_raw) != 32 or len(public_raw) != 32:
        raise RuntimeError(f"invalid external Ed25519 key material for {name}")
    return private_raw, public_raw


def main() -> None:
    issuer_private, issuer_public = ensure_ed25519("issuer-1")
    del issuer_private
    user_private, user_public = ensure_ed25519("user-1")
    del user_private
    origin = datetime(2026, 7, 29, tzinfo=UTC)
    policy = compile_policy(
        [Interval(0, 1440)],
        time_origin=origin,
        delta=timedelta(minutes=1),
        domain_size=1440,
    )
    deployment = json.loads((ROOT / "evidence" / "f7" / "deployment.json").read_text())
    artifact = json.loads((ROOT / "contracts" / "AuthorizationState.json").read_text())
    roles = {
        row["role"]: row["address"]
        for row in json.loads(
            (ROOT / "accounts" / "public-role-addresses.json").read_text(encoding="utf-8-sig")
        )
    }
    address = Web3.to_checksum_address(deployment["contract_address"])
    contract = Web3().eth.contract(address=address, abi=artifact["abi"])
    resource_text = "authorization-resource-001"
    user_text = "authorization-user-001"
    resource_id = Web3.keccak(text=resource_text)
    user_id = Web3.keccak(text=user_text)
    user_key_id = hashlib.sha256(user_public).digest()

    def send(role: str, function: object) -> dict:
        key_path = SECRET_ROOT / role.lower() / "key.hex"
        private_key = key_path.read_text(encoding="ascii").strip()
        sender = Account.from_key(private_key)
        base_fee = int(transport.rpc("eth_getBlockByNumber", ["latest", False])["baseFeePerGas"], 16)
        nonce = int(transport.rpc("eth_getTransactionCount", [sender.address, "pending"]), 16)
        signed = Account.sign_transaction(
            {
                "chainId": CHAIN_ID,
                "nonce": nonce,
                "to": address,
                "data": function._encode_transaction_data(),
                "gas": 500000,
                "maxPriorityFeePerGas": 1,
                "maxFeePerGas": base_fee * 3 + 1,
                "type": 2,
            },
            private_key,
        )
        tx_hash = transport.rpc("eth_sendRawTransaction", [signed.raw_transaction.hex()])
        for _ in range(40):
            receipt = transport.rpc("eth_getTransactionReceipt", [tx_hash])
            if receipt:
                if receipt["status"] != "0x1":
                    raise RuntimeError(f"{role} registration failed")
                return {"transaction_hash": tx_hash, "receipt": receipt}
            time.sleep(2)
        raise TimeoutError(tx_hash)

    resource_tx = send(
        "OWNER",
        contract.functions.registerResource(resource_id, roles["OWNER"], policy.digest),
    )
    user_tx = send(
        "ADMIN",
        contract.functions.registerUser(user_id, roles["AUDITOR"], user_key_id),
    )
    public = {
        "chain_id": CHAIN_ID,
        "contract_address": address,
        "resource_id": resource_text,
        "resource_id_hash": resource_id.hex(),
        "user_id": user_text,
        "user_id_hash": user_id.hex(),
        "policy_digest": policy.digest.hex(),
        "policy_origin": origin.isoformat(),
        "policy_delta_seconds": 60,
        "policy_domain_size": 1440,
        "policy_intervals": [[0, 1440]],
        "issuer_public_key": issuer_public.hex(),
        "user_public_key": user_public.hex(),
        "user_key_id": user_key_id.hex(),
        "resource_registration": resource_tx,
        "user_registration": user_tx,
    }
    target = ROOT / "evidence" / "f8"
    target.mkdir(parents=True, exist_ok=True)
    (target / "service-binding.json").write_text(
        json.dumps(public, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({"resource": resource_text, "user": user_text, "policy_digest": policy.digest.hex()}))


if __name__ == "__main__":
    main()
