"""Generate fresh Formal account roles or a Besu node key. Never logs keys."""
from __future__ import annotations

import argparse
import json

from web3 import Web3


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--node-key", action="store_true")
    args = parser.parse_args()
    if args.node_key:
        account = Web3().eth.account.create()
        print(account.key.hex())
        return
    roles = {}
    for name in ("deployer_admin", "owner", "header_committer", "revocation", "unauthorized"):
        account = Web3().eth.account.create()
        roles[name] = {
            "address": account.address,
            "private_key": account.key.hex(),
        }
    print(json.dumps({"roles": roles}, indent=2))


if __name__ == "__main__":
    main()
