"""Fund formal-chain role accounts using a locally held bootstrap key.

The key path is supplied outside the repository. Transactions are signed locally
and relayed to the controlled RPC endpoint through Windows OpenSSH.
"""

from __future__ import annotations

import base64
import json
import subprocess
import sys
import time
from pathlib import Path

from eth_account import Account

ROOT = Path(__file__).resolve().parents[2]
CHAIN_ID = 2026072901
RPC_HOST = "experiment-client"
RPC_URL = "http://192.168.6.133:8645"


def rpc(method: str, params: list[object]) -> object:
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    encoded = base64.b64encode(body).decode("ascii")
    command = f"echo {encoded} | base64 -d | curl -sS -H 'Content-Type: application/json' --data-binary @- {RPC_URL}"
    result = subprocess.run(["ssh", "-o", "BatchMode=yes", RPC_HOST, command], capture_output=True, text=True, check=True)
    response = json.loads(result.stdout)
    if "error" in response:
        raise RuntimeError(f"RPC {method} failed: {response['error']}")
    return response["result"]


def main(key_path: str) -> None:
    key_file = Path(key_path).resolve()
    if not key_file.is_file() or ROOT in key_file.parents:
        raise ValueError("bootstrap key must be an existing file outside the repository")
    account = Account.from_key(key_file.read_text(encoding="ascii").strip())
    roles = json.loads((ROOT / "accounts" / "public-role-addresses.json").read_text(encoding="utf-8-sig"))
    chain_id = int(rpc("eth_chainId", []), 16)
    if chain_id != CHAIN_ID:
        raise RuntimeError(f"unexpected chain id {chain_id}")
    base_fee = int(rpc("eth_getBlockByNumber", ["latest", False])["baseFeePerGas"], 16)
    priority = max(1, base_fee // 10)
    recipients = [row for row in roles if row["role"] in {"ADMIN", "OWNER", "AUTHORIZER", "REVOCATION"}]
    receipts: list[dict[str, object]] = []
    for row in recipients:
        nonce = int(rpc("eth_getTransactionCount", [account.address, "pending"]), 16)
        tx = {
            "chainId": CHAIN_ID, "nonce": nonce, "to": row["address"], "value": 10**18,
            "gas": 21000, "maxPriorityFeePerGas": priority, "maxFeePerGas": base_fee * 3 + priority, "type": 2,
        }
        signed = Account.sign_transaction(tx, key_file.read_text(encoding="ascii").strip())
        tx_hash = rpc("eth_sendRawTransaction", [signed.raw_transaction.hex()])
        receipt = None
        for _ in range(30):
            receipt = rpc("eth_getTransactionReceipt", [tx_hash])
            if receipt is not None:
                break
            time.sleep(2)
        if receipt is None or receipt.get("status") != "0x1":
            raise RuntimeError(f"funding transaction did not succeed: {tx_hash}")
        receipts.append({"role": row["role"], "recipient": row["address"], "amount_wei": str(10**18), "transaction_hash": tx_hash, "nonce": nonce, "gas_used": receipt["gasUsed"], "block_number": receipt["blockNumber"], "status": receipt["status"]})
    target = ROOT / "evidence" / "f6"
    target.mkdir(parents=True, exist_ok=True)
    (target / "role-funding-receipts.json").write_text(json.dumps({"chain_id": CHAIN_ID, "deployer": account.address, "base_fee_per_gas": str(base_fee), "receipts": receipts}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"funded_roles": [entry["role"] for entry in receipts], "receipt_count": len(receipts)}))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: fund_roles.py <bootstrap-key-file-outside-repository>")
    main(sys.argv[1])
