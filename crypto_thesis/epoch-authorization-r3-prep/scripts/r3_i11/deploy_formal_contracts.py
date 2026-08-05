"""Deploy AuthorizationState + HeaderRegistryV1 onto the independent Formal chain."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from web3 import Web3


def signed_tx(w3: Web3, fn, account: dict, *, chain_id: int) -> dict:
    address = Web3.to_checksum_address(account["address"])
    tx = fn.build_transaction({
        "from": address,
        "nonce": w3.eth.get_transaction_count(address, "pending"),
        "chainId": chain_id,
        "gas": 15_000_000,
        "gasPrice": w3.eth.gas_price,
        "value": 0,
    })
    signed = w3.eth.account.sign_transaction(tx, account["private_key"])
    return dict(w3.eth.wait_for_transaction_receipt(
        w3.eth.send_raw_transaction(signed.raw_transaction), timeout=60
    ))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rpc", required=True)
    parser.add_argument("--chain-id", type=int, required=True)
    parser.add_argument("--accounts", required=True)
    parser.add_argument("--code", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    accounts = json.loads(Path(args.accounts).read_text("utf-8"))["roles"]
    w3 = Web3(Web3.HTTPProvider(args.rpc, request_kwargs={"timeout": 10}))
    if not w3.is_connected() or w3.eth.chain_id != args.chain_id:
        raise RuntimeError("NOT_CONNECTED_TO_FORMAL_CHAIN")
    code = Path(args.code)
    auth_artifact = json.loads(
        (code / "contracts/r3/build/AuthorizationState.json").read_text("utf-8")
    )
    auth_factory = w3.eth.contract(abi=auth_artifact["abi"], bytecode=auth_artifact["bytecode"])
    auth_receipt = signed_tx(
        w3, auth_factory.constructor(), accounts["deployer_admin"], chain_id=args.chain_id
    )
    auth = w3.eth.contract(address=auth_receipt["contractAddress"], abi=auth_artifact["abi"])
    for role_name, account_name in (
        ("OWNER_ROLE", "owner"), ("AUTHORIZER_ROLE", "owner"),
        ("REVOCATION_ROLE", "revocation"),
    ):
        role = auth.functions[role_name]().call()
        signed_tx(
            w3, auth.functions.grantRole(role, accounts[account_name]["address"]),
            accounts["deployer_admin"], chain_id=args.chain_id,
        )
    registry_artifact = json.loads(
        (code / "contracts/r3/build/HeaderRegistryV1.json").read_text("utf-8")
    )
    registry_factory = w3.eth.contract(
        abi=registry_artifact["abi"], bytecode=registry_artifact["bytecode"]
    )
    registry_receipt = signed_tx(
        w3, registry_factory.constructor(auth.address),
        accounts["deployer_admin"], chain_id=args.chain_id,
    )
    registry = w3.eth.contract(
        address=registry_receipt["contractAddress"], abi=registry_artifact["abi"]
    )
    committer_role = registry.functions.HEADER_COMMITTER_ROLE().call()
    signed_tx(
        w3, registry.functions.grantRole(committer_role, accounts["header_committer"]["address"]),
        accounts["deployer_admin"], chain_id=args.chain_id,
    )
    auth_address = Web3.to_checksum_address(auth.address)
    registry_address = Web3.to_checksum_address(registry.address)
    result = {
        "schemaVersion": "R3FormalContractsV1",
        "chainId": args.chain_id,
        "auth": auth_address,
        "registry": registry_address,
        "authDeployBlock": int(auth_receipt["blockNumber"]),
        "registryDeployBlock": int(registry_receipt["blockNumber"]),
    }
    Path(args.out).write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
