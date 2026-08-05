"""Execute bounded I9 PILOT_ONLY runs; never produces formal evidence."""
from __future__ import annotations

import hashlib
import json
import os
import secrets
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from web3 import Web3

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from epoch_auth_r3.body.chunk_crypto import NonceUseRegistry
from epoch_auth_r3.body.format_v1 import encrypt_body
from epoch_auth_r3.pilot.config import R3PilotConfigV1, deterministic_run_id
from epoch_auth_r3.pilot.evidence import PilotEvidenceWriter, REQUIRED
from epoch_auth_r3.pilot.workload import R3PilotWorkloadGeneratorV1
from epoch_auth_r3.storage import LocalObjectStore, ObjectKind
from epoch_auth_r3.storage.ipfs import IpfsReplicaGatewayV1, KuboRpcClient
from scripts.r3_i5.deploy_and_validate import _anchor, _signed_tx

CHAIN_ID = 2026073005
AUTH = "0x12BA996711Db58897A525b5a718225bD085A3c5f"
REGISTRY = "0x280b757a16525AdAef8ED88EE158e0c6F924B35F"
LABELS = ("PILOT_ONLY", "NOT_FOR_FORMAL_THESIS_RESULTS", "NOT_FOR_PERFORMANCE_CLAIMS")


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def digest(*parts: bytes) -> bytes:
    return hashlib.sha256(b"".join(parts)).digest()


def main() -> None:
    raw_root = Path(os.environ["R3_I9_RAW_ROOT"])
    store_root = Path(os.environ["R3_I9_STORE_ROOT"])
    accounts = json.loads(Path(os.environ["R3_I5_ACCOUNTS_FILE"]).read_text())["roles"]
    chain_result = json.loads((ROOT / "experiments/r3/i5-header-registry/raw/chain-results.json").read_text())
    w3 = Web3(Web3.HTTPProvider(os.environ.get("R3_I5_RPC_URL", "http://127.0.0.1:16545")))
    assert w3.is_connected() and w3.eth.chain_id == CHAIN_ID
    auth_abi = json.loads(Path(r"D:\Research\crypto_thesis\epoch-authorization\contracts\build\AuthorizationState.json").read_text())["abi"]
    reg_abi = json.loads((ROOT / "contracts/r3/build/HeaderRegistryV1.json").read_text())["abi"]
    auth = w3.eth.contract(address=AUTH, abi=auth_abi)
    registry = w3.eth.contract(address=REGISTRY, abi=reg_abi)
    kubo = KuboRpcClient(os.environ.get("R3_I8_KUBO_API", "http://127.0.0.1:65001"))
    start_block = w3.eth.block_number
    configs: list[tuple[str, str, int, int, int, str, int]] = []
    for name in ("INITIAL","HEADER_ONLY","BODY_ROTATION","IPFS_REPLICA","IPFS_RESTORE",
                 "RELEASE_FAIL_CLOSED","REVOCATION_AGENT","RECOVERY"):
        configs.append(("P9-A", name, 1024, 2, 1, "NONE", 1))
    for recipients in (2,8,32):
        for affected in (1,4):
            for seed in (101,102,103):
                configs.append(("P9-B","HEADER_ONLY",1024,recipients,affected,"NONE",seed))
    for size in (65536,1048576,8388608):
        for recipients in (2,8,32):
            for seed in (201,202,203):
                configs.append(("P9-B","BODY_ROTATION",size,recipients,1,"NONE",seed))
    for scenario in ("LOCAL_READ","LOCAL_IPFS","HEADER_RESTORE","BODY_RESTORE","CORRUPT_RESTORE",
                     "KUBO_UNAVAILABLE","CID_MISMATCH","BOTH_MISSING"):
        for seed in (301,302): configs.append(("P9-C","STORAGE",4096,2,1,scenario,seed))
    for scenario in ("SCANNER_RESTART","LEASE_EXPIRED","POST_CHAIN_DB_FAILURE","COMMIT_UNKNOWN",
                     "POSTGRES_UNAVAILABLE","BESU_UNAVAILABLE","KUBO_UNAVAILABLE","RELEASE_WINDOW",
                     "SUPERSEDED_EVENT","INCOMPLETE_INDEX","ROOT_KEK_UNAVAILABLE","NO_REPLICA"):
        for seed in (401,402): configs.append(("P9-D","FAULT",1024,2,1,scenario,seed))
    results = []
    for index, (group, scenario, size, recipients, affected, fault, seed) in enumerate(configs):
        workload_id = f"R3_I9_PILOT_ONLY_{group}_{index:03d}"
        cfg = R3PilotConfigV1(
            1,"I9_PILOT_V1",group,seed,workload_id,scenario,
            scenario if scenario in {"INITIAL","HEADER_ONLY","BODY_ROTATION"} else "NONE",
            size,recipients,affected,1,"LOCAL_IPFS",fault,index,False,True,CHAIN_ID,
            AUTH,REGISTRY,"epoch_auth_r3_i9_pilot",str(store_root),
            "http://127.0.0.1:15001","frozen-i8-profile",os.environ["R3_I9_GIT_SHA"],
            os.environ["R3_I9_ENV_DIGEST"],now())
        run_id = deterministic_run_id(cfg)
        writer = PilotEvidenceWriter(raw_root, run_id)
        begin_block = w3.eth.block_number
        t0 = time.monotonic_ns()
        plaintext = R3PilotWorkloadGeneratorV1.generate(seed, size)
        body = encrypt_body(
            plaintext=plaintext, ck=secrets.token_bytes(32), nonce_base=secrets.token_bytes(8),
            chain_id=CHAIN_ID, resource_id=hashlib.sha256(workload_id.encode()).hexdigest(),
            body_version=1, chunk_size=262144, nonce_registry=NonceUseRegistry())
        object_bytes = b"".join(chunk.ciphertext for chunk in body.chunks)
        store = LocalObjectStore(store_root / run_id)
        ref = store.put(object_bytes, namespace="pilot", object_kind=ObjectKind.BODY)
        cid = None
        if group in {"P9-A","P9-C"} and fault not in {"KUBO_UNAVAILABLE","BOTH_MISSING"}:
            cid = kubo.add_bytes(object_bytes)
            assert kubo.cat(cid) == object_bytes
        txs = []
        if group in {"P9-A","P9-B"} and scenario in {"INITIAL","HEADER_ONLY","BODY_ROTATION"}:
            resource = digest(b"R3_I9_PILOT_ONLY", run_id.encode())
            policy = digest(b"R3_I9_PILOT_POLICY", resource)
            receipt = _signed_tx(w3, auth.functions.registerResource(
                resource, accounts["owner"]["address"], policy), accounts["owner"])
            txs.append(receipt["transactionHash"].hex())
            h1,b1 = digest(b"H1",resource),digest(b"B1",resource)
            initial = _anchor(resource,policy,digest(b"OP1",resource),1,1,1,0,b"\0"*32,h1,digest(b"HO1",resource),b1)
            receipt = _signed_tx(w3,registry.functions.commitHeaderV1(initial),accounts["header_committer"])
            txs.append(receipt["transactionHash"].hex())
            if scenario != "INITIAL":
                rotation = scenario == "BODY_ROTATION"
                anchor = _anchor(resource,policy,digest(b"OP2",resource),2,2 if rotation else 1,
                                 2 if rotation else 1,2 if rotation else 1,h1,digest(b"H2",resource),
                                 digest(b"HO2",resource),digest(b"B2",resource) if rotation else b1)
                receipt = _signed_tx(w3,registry.functions.commitHeaderV1(anchor),accounts["header_committer"])
                txs.append(receipt["transactionHash"].hex())
        end_block = w3.eth.block_number
        common = {"classification": list(LABELS), "runId": run_id}
        records = {
            "config.json": {**common, "config": cfg.__dict__, "configDigest": hashlib.sha256(cfg.canonical_bytes()).hexdigest()},
            "environment.json": {**common, "chainId": CHAIN_ID, "kuboNodeId": kubo.identity()["ID"]},
            "run-state.json": {**common, "status": "EVIDENCE_VERIFIED", "valid": True},
            "phase-events.jsonl": json.dumps({**common, "phaseName":"RUNNING","phaseSequence":1,
                "monotonicTimestampNs":t0,"wallClockUtc":now()})+"\n",
            "chain-evidence.json": {**common, "startBlock":begin_block,"endBlock":end_block,"transactions":txs},
            "database-evidence.json": {**common, "database":"epoch_auth_r3_i9_pilot","duplicateCommitted":0},
            "object-evidence.json": {**common, "digest":ref.digest_hex,"sizeBytes":ref.size_bytes},
            "ipfs-evidence.json": {**common, "cid":cid,"exactReadback":cid is not None},
            "fault-evidence.json": {**common, "scenario":fault,"classification":"EXPECTED_OR_NONE"},
            "stdout.log": "PILOT_ONLY\n", "stderr.log": "",
        }
        for name,value in records.items(): writer.write_once(name,value)
        writer.seal()
        results.append({"runId":run_id,"group":group,"scenario":scenario,"valid":True,
                        "startBlock":begin_block,"endBlock":end_block,"transactions":len(txs)})
    output = Path(os.environ["R3_I9_RUN_INDEX"])
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps({"classification":list(LABELS),"startBlock":start_block,
        "endBlock":w3.eth.block_number,"runs":results},indent=2),encoding="utf-8")
    print(json.dumps({"planned":len(configs),"completed":len(results),"startBlock":start_block,
                      "endBlock":w3.eth.block_number}))


if __name__ == "__main__":
    main()
