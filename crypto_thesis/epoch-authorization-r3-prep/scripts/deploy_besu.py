"""Deploy AuthorizationState and grant prototype roles on the local Besu network."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from web3 import Web3

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "contracts" / "build" / "AuthorizationState.json"
DEPLOYMENT = ROOT / "blockchain" / "besu" / "deployment.json"
RPC_URL = "http://127.0.0.1:8545"
CHAIN_ID = 20260728

# Deterministic Anvil/eth-tester development key. Never use outside this local prototype.
DEV_PRIVATE_KEY = "0x" + "00" * 31 + "01"


def send(web3: Web3, function: object, private_key: str) -> dict:
    """Sign, submit, and await one local-chain transaction."""

    account = web3.eth.account.from_key(private_key)
    tx = function.build_transaction(
        {
            "from": account.address,
            "chainId": web3.eth.chain_id,
            "nonce": web3.eth.get_transaction_count(account.address, "pending"),
            "gasPrice": web3.eth.gas_price,
        }
    )
    signed = web3.eth.account.sign_transaction(tx, private_key)
    tx_hash = web3.eth.send_raw_transaction(signed.raw_transaction)
    receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)
    if receipt["status"] != 1:
        raise RuntimeError(f"transaction failed: {tx_hash.hex()}")
    return dict(receipt)


def main() -> None:
    """Deploy the frozen artifact and write a machine-readable deployment record."""

    web3 = Web3(Web3.HTTPProvider(RPC_URL, request_kwargs={"timeout": 10}))
    if not web3.is_connected():
        raise RuntimeError(f"Besu RPC is unavailable at {RPC_URL}")
    if web3.eth.chain_id != CHAIN_ID:
        raise RuntimeError(f"unexpected chain id: {web3.eth.chain_id}")

    artifact_bytes = ARTIFACT.read_bytes()
    artifact = json.loads(artifact_bytes)
    account = web3.eth.account.from_key(DEV_PRIVATE_KEY)
    factory = web3.eth.contract(abi=artifact["abi"], bytecode=artifact["bytecode"])
    receipt = send(web3, factory.constructor(), DEV_PRIVATE_KEY)
    address = Web3.to_checksum_address(receipt["contractAddress"])
    contract = web3.eth.contract(address=address, abi=artifact["abi"])

    roles = ("OWNER_ROLE", "AUTHORIZER_ROLE", "REVOCATION_ROLE", "AUDITOR_ROLE")
    role_transactions: dict[str, str] = {}
    for role_name in roles:
        role = getattr(contract.functions, role_name)().call()
        role_receipt = send(
            web3, contract.functions.grantRole(role, account.address), DEV_PRIVATE_KEY
        )
        role_transactions[role_name] = role_receipt["transactionHash"].hex()

    record = {
        "rpc_url": RPC_URL,
        "chain_id": web3.eth.chain_id,
        "contract_name": "AuthorizationState",
        "contract_address": address,
        "deployer": account.address,
        "deployment_block": receipt["blockNumber"],
        "deployment_transaction": receipt["transactionHash"].hex(),
        "artifact_sha256": hashlib.sha256(artifact_bytes).hexdigest(),
        "role_transactions": role_transactions,
    }
    DEPLOYMENT.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
