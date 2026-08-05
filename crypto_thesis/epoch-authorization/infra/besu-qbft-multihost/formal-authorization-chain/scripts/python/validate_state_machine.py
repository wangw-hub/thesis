"""Exercise AuthorizationState roles and irreversible transitions on the formal chain."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

from eth_account import Account
from web3 import Web3

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fund_roles as transport

ROOT = Path(__file__).resolve().parents[2]
SECRET_ROOT = Path(r"D:\Research\crypto_thesis\secrets\formal-authorization-chain-2026072901")
CHAIN_ID = 2026072901


def key_for(role: str) -> str:
    path = SECRET_ROOT / role.lower().replace("_", "-") / "key.hex"
    if not path.is_file() or ROOT in path.resolve().parents:
        raise RuntimeError(f"missing external key for {role}")
    return path.read_text(encoding="ascii").strip()


def wait_receipt(tx_hash: str) -> dict:
    for _ in range(40):
        receipt = transport.rpc("eth_getTransactionReceipt", [tx_hash])
        if receipt:
            return receipt
        time.sleep(2)
    raise TimeoutError(tx_hash)


def main() -> None:
    artifact = json.loads((ROOT / "contracts" / "AuthorizationState.json").read_text())
    deployment = json.loads((ROOT / "evidence" / "f7" / "deployment.json").read_text())
    roles = {
        row["role"]: row["address"]
        for row in json.loads(
            (ROOT / "accounts" / "public-role-addresses.json").read_text(encoding="utf-8-sig")
        )
    }
    address = Web3.to_checksum_address(deployment["contract_address"])
    contract = Web3().eth.contract(address=address, abi=artifact["abi"])
    resource_id = Web3.keccak(text="formal-resource-001")
    policy_1 = Web3.keccak(text="formal-policy-i-star-v1")
    reason = Web3.keccak(text="formal-epoch-advance")
    user_id = Web3.keccak(text="formal-user-001")
    key_1 = Web3.keccak(text="formal-user-key-v1")
    key_2 = Web3.keccak(text="formal-user-key-v2")
    records: list[dict] = []

    def send(role: str, function: object, expected_status: int) -> dict:
        private_key = key_for(role)
        sender = Account.from_key(private_key)
        base_fee = int(transport.rpc("eth_getBlockByNumber", ["latest", False])["baseFeePerGas"], 16)
        nonce = int(transport.rpc("eth_getTransactionCount", [sender.address, "pending"]), 16)
        tx = {
            "chainId": CHAIN_ID,
            "nonce": nonce,
            "to": address,
            "data": function._encode_transaction_data(),
            "gas": 500000,
            "maxPriorityFeePerGas": 1,
            "maxFeePerGas": base_fee * 3 + 1,
            "type": 2,
        }
        signed = Account.sign_transaction(tx, private_key)
        tx_hash = transport.rpc("eth_sendRawTransaction", [signed.raw_transaction.hex()])
        receipt = wait_receipt(tx_hash)
        actual = int(receipt["status"], 16)
        item = {
            "role": role,
            "function": function.fn_name,
            "expected_status": expected_status,
            "actual_status": actual,
            "transaction_hash": tx_hash,
            "block_number": receipt["blockNumber"],
            "gas_used": receipt["gasUsed"],
        }
        records.append(item)
        if actual != expected_status:
            raise RuntimeError(f"unexpected status for {role}.{function.fn_name}: {actual}")
        return receipt

    send("OWNER", contract.functions.registerResource(resource_id, roles["OWNER"], policy_1), 1)
    send("AUDITOR", contract.functions.registerResource(Web3.keccak(text="forbidden"), roles["AUDITOR"], policy_1), 0)
    send("AUTHORIZER", contract.functions.advanceEpoch(resource_id, reason), 1)
    send("OWNER", contract.functions.advanceEpoch(resource_id, reason), 0)
    send("REVOCATION", contract.functions.suspendResource(resource_id), 1)
    send("REVOCATION", contract.functions.activateResource(resource_id), 1)
    send("REVOCATION", contract.functions.revokeResource(resource_id), 1)
    send("REVOCATION", contract.functions.activateResource(resource_id), 0)
    send("ADMIN", contract.functions.registerUser(user_id, roles["AUDITOR"], key_1), 1)
    send("ADMIN", contract.functions.rotateUserKey(user_id, key_2), 1)
    send("ADMIN", contract.functions.registerUser(Web3.keccak(text="duplicate-user"), roles["AUDITOR"], key_2), 0)
    send("REVOCATION", contract.functions.suspendUser(user_id), 1)
    send("REVOCATION", contract.functions.activateUser(user_id), 1)
    send("REVOCATION", contract.functions.revokeUser(user_id), 1)
    send("REVOCATION", contract.functions.activateUser(user_id), 0)

    def call(function: object) -> str:
        result = transport.rpc("eth_call", [{"to": address, "data": function._encode_transaction_data()}, "latest"])
        return result

    summary = {
        "chain_id": CHAIN_ID,
        "contract_address": address,
        "transactions": records,
        "resource_raw": call(contract.functions.getResource(resource_id)),
        "user_raw": call(contract.functions.getUser(user_id)),
        "unexpected_status_count": sum(x["expected_status"] != x["actual_status"] for x in records),
        "permission_bypass_count": 0,
    }
    target = ROOT / "evidence" / "f7"
    (target / "state-machine-validation.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({"transactions": len(records), "unexpected_status_count": 0}))


if __name__ == "__main__":
    main()
