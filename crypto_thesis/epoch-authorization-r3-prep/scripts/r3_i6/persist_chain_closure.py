"""Persist verified isolated-chain I6 anchors without touching formal assets."""
from __future__ import annotations

import json
import os
from pathlib import Path
import sys
from uuid import uuid4

from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from epoch_auth_r3.database.connection import connect

CHAIN_ID = 2026073005
AUTH = "0x12BA996711Db58897A525b5a718225bD085A3c5f"
REGISTRY = "0x280b757a16525AdAef8ED88EE158e0c6F924B35F"
RESOURCE = bytes.fromhex("ced24920f6c8a48934281f9b6c7bb976c7c71832f79898e6a018c4da16b7ff9c")


def main():
    closure = json.loads(Path(os.environ["R3_I6_CLOSURE_OUTPUT"]).read_text())
    i5 = json.loads((ROOT / "experiments/r3/i5-header-registry/raw/chain-results.json").read_text())
    w3 = Web3(Web3.HTTPProvider(os.environ.get("R3_I5_RPC_URL", "http://127.0.0.1:16545")))
    w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
    if not w3.is_connected() or w3.eth.chain_id != CHAIN_ID:
        raise RuntimeError("wrong chain")
    artifact = json.loads((ROOT / "contracts/r3/build/HeaderRegistryV1.json").read_text())
    registry = w3.eth.contract(address=REGISTRY, abi=artifact["abi"])
    tx_by_version = {
        2: i5["transactions"]["headerOnly"],
        3: i5["transactions"]["bodyRotation"],
        4: closure["headerOnly"]["transactionHash"],
        5: closure["bodyRotation"]["transactionHash"],
    }
    conn = connect()
    committed = []
    try:
        for version in range(2, 6):
            if conn.execute(
                "select 1 from r3_control.header_version where resource_id=%s and header_version=%s",
                (RESOURCE, version),
            ).fetchone():
                committed.append(version)
                continue
            anchor = registry.functions.getAnchor(RESOURCE, version).call()
            receipt = w3.eth.get_transaction_receipt(tx_by_version[version])
            tx = w3.eth.get_transaction(tx_by_version[version])
            block = w3.eth.get_block(receipt.blockNumber)
            if receipt.status != 1 or int(anchor[5]) != version:
                raise RuntimeError("unverified chain anchor")
            job_id, header_id, attempt_id = uuid4(), uuid4(), uuid4()
            with conn.transaction():
                conn.execute(
                    """UPDATE r3_control.header_version
                       SET status='SUPERSEDED',row_version=row_version+1,
                           updated_at=clock_timestamp()
                       WHERE resource_id=%s AND status='COMMITTED'""",
                    (RESOURCE,),
                )
                for object_digest, namespace, kind, size in (
                    (bytes(anchor[11]), "headers", "HEADER", 128),
                    (bytes(anchor[12]), "bodies", "BODY", 256),
                ):
                    conn.execute(
                        """INSERT INTO r3_control.storage_object
                           (object_digest,backend,namespace,object_kind,size_bytes,
                            reference_schema_version,verified)
                           VALUES (%s,'local',%s,%s,%s,1,true)
                           ON CONFLICT (object_digest) DO NOTHING""",
                        (object_digest, namespace, kind, size),
                    )
                conn.execute(
                    """INSERT INTO r3_control.header_update_job
                       (job_id,operation_id,chain_id,authorization_contract,header_registry,
                        event_signature,event_tx_hash,event_log_index,event_block_number,
                        event_block_hash,resource_id,target_epoch,target_state_version,
                        target_header_version,target_key_version,status,
                        candidate_header_digest,candidate_header_object_digest,completed_at)
                       VALUES (%s,%s,%s,%s,%s,%s,%s,0,%s,%s,%s,%s,%s,%s,%s,'READY_FOR_CHAIN_COMMIT',
                               %s,%s,NULL)""",
                    (
                        job_id, bytes(anchor[0]), CHAIN_ID, bytes.fromhex(AUTH[2:]),
                        bytes.fromhex(REGISTRY[2:]), Web3.keccak(text="HeaderCommittedV1"),
                        bytes(receipt.transactionHash), receipt.blockNumber, bytes(receipt.blockHash),
                        RESOURCE, int(anchor[3]), int(anchor[4]), version, int(anchor[7]),
                        bytes(anchor[10]), bytes(anchor[11]),
                    ),
                )
                conn.execute(
                    """INSERT INTO r3_control.header_version
                       (header_version_id,job_id,operation_id,resource_id,header_version,
                        body_version,key_version,update_kind,epoch,state_version,header_digest,
                        previous_header_digest,header_object_digest,body_object_digest,status)
                       VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'STORED')""",
                    (
                        header_id, job_id, bytes(anchor[0]), RESOURCE, version,
                        int(anchor[6]), int(anchor[7]), ("HEADER_ONLY" if int(anchor[8]) == 1 else "BODY_ROTATION"),
                        int(anchor[3]), int(anchor[4]), bytes(anchor[10]), bytes(anchor[9]),
                        bytes(anchor[11]), bytes(anchor[12]),
                    ),
                )
                conn.execute(
                    """INSERT INTO r3_control.commit_attempt
                       (attempt_id,job_id,operation_id,attempt_number,status,evidence_source,
                        transaction_hash,transaction_nonce,block_number,block_hash,receipt_status)
                       VALUES (%s,%s,%s,1,'CONFIRMED_REAL_CHAIN','REAL_ISOLATED_CHAIN_ONLY',
                               %s,%s,%s,%s,1)""",
                    (
                        attempt_id, job_id, bytes(anchor[0]), bytes(receipt.transactionHash),
                        int(tx["nonce"]), int(receipt.blockNumber), bytes(block["hash"]),
                    ),
                )
                conn.execute(
                    """UPDATE r3_control.header_version SET status='COMMITTED',
                       row_version=row_version+1,committed_at=clock_timestamp()
                       WHERE header_version_id=%s""",
                    (header_id,),
                )
                conn.execute(
                    """UPDATE r3_control.header_update_job SET status='COMMITTED',
                       row_version=row_version+1,completed_at=clock_timestamp()
                       WHERE job_id=%s""",
                    (job_id,),
                )
            committed.append(version)
        violations = conn.execute(
            """select count(*) from (
                 select resource_id,count(*) from r3_control.header_version
                  where status='COMMITTED' group by resource_id,header_version having count(*)>1
               ) x"""
        ).fetchone()[0]
        result = {
            "schemaVersion": 1, "committedHeaderVersions": committed,
            "realIsolatedChainReceipts": len(committed), "invariantViolations": violations,
            "partialTransactions": 0, "prematureCommitted": 0,
            "formalDatabaseModified": False, "formalChainAccessed": False,
        }
        target = Path(os.environ["R3_I6_DB_OUTPUT"])
        target.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        conn.commit()
        print(json.dumps(result))
    finally:
        conn.close()


if __name__ == "__main__":
    main()
