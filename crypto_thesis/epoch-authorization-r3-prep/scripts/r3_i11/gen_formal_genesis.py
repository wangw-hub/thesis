"""Generate the independent Formal QBFT genesis-input (Besu operator format)."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from web3 import Web3

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--chain-id", type=int, required=True)
    parser.add_argument("--accounts", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    accounts = json.loads(Path(args.accounts).read_text("utf-8"))["roles"]
    alloc = {
        Web3.to_checksum_address(account["address"]): {"balance": "0x21e19e0c9bab2400000"}
        for account in accounts.values()
    }
    genesis_input = {
        "genesis": {
            "config": {
                "chainId": args.chain_id,
                "berlinBlock": 0,
                "londonBlock": 0,
                "qbft": {"blockperiodseconds": 2, "epochlength": 30000,
                         "requesttimeoutseconds": 4},
            },
            "nonce": "0x0",
            "timestamp": "0x0",
            "gasLimit": "0x1fffffffffffff",
            "difficulty": "0x1",
            "mixHash": "0x7263345f666f726d616c5f636861696e5f763100000000000000000000",
            "coinbase": "0x0000000000000000000000000000000000000000",
            "alloc": alloc,
        },
        "blockchain": {
            "nodes": {"generate": True, "count": 1},
        },
    }
    Path(args.out).write_text(json.dumps(genesis_input, indent=2), encoding="utf-8")
    print(json.dumps({"chainId": args.chain_id, "genesisInput": str(args.out),
                      "allocAccounts": len(alloc)}, sort_keys=True))


if __name__ == "__main__":
    main()
