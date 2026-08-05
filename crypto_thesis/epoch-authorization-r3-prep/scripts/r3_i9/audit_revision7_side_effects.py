from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from web3 import Web3

from epoch_auth_r3.blockchain import CompositeStateGateway
from epoch_auth_r3.blockchain.web3_factory import BesuQbftWeb3FactoryV1
from scripts.r3_i9.run_revised_remote_pilot import (
    AUTH, AUTH_ABI, CHAIN_ID, REGISTRY,
)


def hex_value(value) -> str:
    if isinstance(value, str):
        return value.removeprefix("0x").lower()
    return bytes(value).hex()


def decoded_operation_id(decoded: dict) -> str:
    anchor = next(iter(decoded.values()))
    if isinstance(anchor, dict):
        return hex_value(anchor["operationId"])
    return hex_value(anchor[0])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--attempt-id", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--from-block", required=True, type=int)
    parser.add_argument("--to-block", required=True, type=int)
    parser.add_argument("--registry-artifact", type=Path, required=True)
    args = parser.parse_args()
    if args.to_block < args.from_block or args.to_block - args.from_block > 32:
        raise SystemExit("UNBOUNDED_REVISION7_AUDIT")

    resource_hex = hashlib.sha256(
        f"{args.attempt_id}:{args.run_id}".encode()
    ).hexdigest()
    resource = bytes.fromhex(resource_hex)
    job_operation_id = hashlib.sha256(
        b"R3_I9_CANARY_OPERATION_V1\x00" + args.run_id.encode()
    ).hexdigest()
    chain_operation_id = hashlib.sha256(b"OP1" + resource).hexdigest()
    w3 = BesuQbftWeb3FactoryV1.create(
        "http://127.0.0.1:18545", expected_chain_id=CHAIN_ID, request_timeout=5,
    )
    registry_abi = json.loads(args.registry_artifact.read_text())["abi"]
    auth = w3.eth.contract(address=AUTH, abi=AUTH_ABI)
    registry = w3.eth.contract(address=REGISTRY, abi=registry_abi)
    candidates = []
    for number in range(args.from_block, args.to_block + 1):
        block = w3.eth.get_block(number, full_transactions=True)
        for tx in block["transactions"]:
            target = tx.get("to")
            if not target or Web3.to_checksum_address(target) not in {
                Web3.to_checksum_address(AUTH), Web3.to_checksum_address(REGISTRY)
            }:
                continue
            input_hex = hex_value(tx["input"])
            if resource_hex not in input_hex:
                continue
            receipt = w3.eth.get_transaction_receipt(tx["hash"])
            contract = auth if Web3.to_checksum_address(target) == Web3.to_checksum_address(AUTH) else registry
            fn, decoded = contract.decode_function_input(tx["input"])
            candidates.append({
                "transactionHash": hex_value(tx["hash"]),
                "sender": tx["from"],
                "nonce": int(tx["nonce"]),
                "to": tx["to"],
                "inputDigest": hashlib.sha256(bytes.fromhex(input_hex)).hexdigest(),
                "blockNumber": int(receipt["blockNumber"]),
                "blockHash": hex_value(receipt["blockHash"]),
                "transactionIndex": int(receipt["transactionIndex"]),
                "receiptStatus": int(receipt["status"]),
                "gasUsed": int(receipt["gasUsed"]),
                "logCount": len(receipt["logs"]),
                "contractMethod": fn.fn_name,
                "decodedOperationId": (
                    decoded_operation_id(decoded)
                    if fn.fn_name == "commitHeaderV1" else None
                ),
            })
    if len(candidates) != 2:
        raise SystemExit(f"REVISION7_TRANSACTION_RESOLUTION_COUNT:{len(candidates)}")
    fixed_block = max(item["blockNumber"] for item in candidates)
    composite = CompositeStateGateway(w3, auth, registry).read(
        resource, block_identifier=fixed_block,
    )
    auth_state = auth.functions.getResource(resource).call(
        block_identifier=fixed_block
    )
    print(json.dumps({
        "schemaVersion": 1,
        "classification": "AUDIT_ONLY",
        "attemptId": args.attempt_id,
        "runId": args.run_id,
        "resourceId": resource_hex,
        "jobOperationId": job_operation_id,
        "chainOperationId": chain_operation_id,
        "boundedRange": [args.from_block, args.to_block],
        "transactions": candidates,
        "fixedBlock": fixed_block,
        "authorizationState": {
            "owner": auth_state[0],
            "policyDigest": hex_value(auth_state[1]),
            "epoch": int(auth_state[2]),
            "status": int(auth_state[3]),
            "stateVersion": int(auth_state[5]),
        },
        "compositeState": {
            "status": composite.status.value,
            "blockNumber": composite.block_number,
            "blockHash": composite.block_hash,
            "headerVersion": composite.header_version,
            "bodyVersion": composite.body_version,
            "keyVersion": composite.key_version,
            "headerDigest": hex_value(composite.header_digest),
            "headerObjectDigest": hex_value(composite.header_object_digest),
            "bodyObjectDigest": hex_value(composite.body_object_digest),
        },
    }, sort_keys=True))


if __name__ == "__main__":
    main()
