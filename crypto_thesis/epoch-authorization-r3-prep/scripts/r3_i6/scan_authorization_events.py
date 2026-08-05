"""Bounded real-event backfill on the isolated I5 chain only."""
from __future__ import annotations

import json
import os
from pathlib import Path
import sys

from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from epoch_auth_r3.database.connection import connect
from epoch_auth_r3.revocation.repository import AuthorizationEventRepository
from epoch_auth_r3.revocation.scanner import AuthorizationEventScanner

CHAIN_ID = 2026073005
AUTH = "0x12BA996711Db58897A525b5a718225bD085A3c5f"
MAIN = Path(r"D:\Research\crypto_thesis\epoch-authorization")


def main() -> None:
    w3 = Web3(Web3.HTTPProvider(os.environ.get("R3_I5_RPC_URL", "http://127.0.0.1:16545")))
    w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
    if not w3.is_connected() or w3.eth.chain_id != CHAIN_ID:
        raise RuntimeError("isolated I5 chain identity mismatch")
    artifact = json.loads(
        (MAIN / "contracts/build/AuthorizationState.json").read_text(encoding="utf-8")
    )
    contract = w3.eth.contract(address=AUTH, abi=artifact["abi"])
    state_reads = []

    def observe(name, args, block):
        if "resourceId" in args:
            record = contract.functions.getResource(args["resourceId"]).call(block_identifier=block)
            state_reads.append({
                "event": name, "block": block, "epoch": int(record[2]),
                "status": int(record[3]), "stateVersion": int(record[5]),
            })
        elif "userId" in args:
            record = contract.functions.getUser(args["userId"]).call(block_identifier=block)
            state_reads.append({
                "event": name, "block": block, "status": int(record[2]),
                "userVersion": int(record[3]),
            })

    conn = connect()
    try:
        scanner = AuthorizationEventScanner(
            w3, contract, AuthorizationEventRepository(conn), state_observer=observe
        )
        start = int(os.environ.get("R3_I6_SCAN_START", "825"))
        end = int(os.environ.get("R3_I6_SCAN_END", str(w3.eth.block_number)))
        with conn.transaction():
            result = scanner.backfill_once(start, end)
        output = {
            "schemaVersion": 1,
            "chainId": CHAIN_ID,
            "authorizationContract": AUTH,
            "startBlock": result.start_block,
            "endBlock": result.end_block,
            "observed": result.observed,
            "inserted": result.inserted,
            "duplicates": result.duplicates,
            "stateReadsAtEventBlock": state_reads,
            "formalChainAccessed": False,
        }
        target = Path(os.environ["R3_I6_SCAN_OUTPUT"])
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({k: output[k] for k in ("startBlock","endBlock","observed","inserted","duplicates")}))
    finally:
        conn.close()


if __name__ == "__main__":
    main()
