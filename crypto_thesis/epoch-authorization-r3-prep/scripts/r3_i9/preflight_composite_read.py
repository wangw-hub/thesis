"""Read-only CompositeStateDecoder preflight for the isolated I5 chain."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from epoch_auth_r3.blockchain import CompositeReadStatus, CompositeStateGateway
from epoch_auth_r3.blockchain.web3_factory import BesuQbftWeb3FactoryV1
from scripts.r3_i9.run_revised_remote_pilot import AUTH_ABI


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--resource-id", required=True)
    parser.add_argument("--authorization", required=True)
    parser.add_argument("--registry", required=True)
    args = parser.parse_args()
    w3 = BesuQbftWeb3FactoryV1.create("http://127.0.0.1:18545", expected_chain_id=2026073005)
    auth = w3.eth.contract(address=args.authorization, abi=AUTH_ABI)
    root = Path(__file__).resolve().parents[2]
    registry_abi = json.loads((root / "contracts/r3/build/HeaderRegistryV1.json").read_text("utf-8"))["abi"]
    registry = w3.eth.contract(address=args.registry, abi=registry_abi)
    result = CompositeStateGateway(w3, auth, registry).read(bytes.fromhex(args.resource_id))
    if result.status is not CompositeReadStatus.CONFIRMED:
        raise SystemExit(f"COMPOSITE_PREFLIGHT_FAILED:{result.failure_code}")
    print(json.dumps({"status": result.status.value, "blockNumber": result.block_number,
                      "resourceId": result.resource_id.hex(), "headerVersion": result.header_version,
                      "bodyVersion": result.body_version, "keyVersion": result.key_version}, sort_keys=True))


if __name__ == "__main__":
    main()
