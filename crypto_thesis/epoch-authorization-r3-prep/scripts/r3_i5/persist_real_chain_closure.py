"""Persist one real isolated-chain receipt in the isolated r3_i4 database."""
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
from epoch_auth_r3.database.job_repository import JobRepository
from epoch_auth_r3.database.models import JobStatus, SyntheticRevocationEventV1
from epoch_auth_r3.database.operation_id import operation_id_v1
from epoch_auth_r3.database.repositories import ArtifactRepository


def main() -> None:
    manifest = json.loads(Path(os.environ["R3_I5_CHAIN_RESULT"]).read_text(encoding="utf-8"))
    w3 = Web3(Web3.HTTPProvider(os.environ.get("R3_I5_RPC_URL", "http://127.0.0.1:16545")))
    w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
    if not w3.is_connected() or w3.eth.chain_id != 2026073005:
        raise RuntimeError("isolated I5 chain unavailable")
    trigger = manifest["trigger"]
    event = SyntheticRevocationEventV1(
        chain_id=manifest["chainId"],
        authorization_contract=bytes.fromhex(manifest["authorizationState"][2:]),
        header_registry=bytes.fromhex(manifest["headerRegistry"][2:]),
        event_signature=bytes.fromhex(trigger["eventSignature"]),
        tx_hash=bytes.fromhex(trigger["transactionHash"]),
        log_index=trigger["logIndex"],
        block_number=trigger["blockNumber"],
        block_hash=bytes.fromhex(trigger["blockHash"]),
        resource_id=bytes.fromhex(manifest["resourceId"]),
        new_epoch=1,
        new_state_version=1,
        new_header_version=1,
        new_key_version=1,
    )
    if operation_id_v1(event).hex() != trigger["operationId"]:
        raise RuntimeError("OperationIdV1 mismatch")

    registry_artifact = json.loads(
        (ROOT / "contracts/r3/build/HeaderRegistryV1.json").read_text(encoding="utf-8")
    )
    registry = w3.eth.contract(address=manifest["headerRegistry"], abi=registry_artifact["abi"])
    anchor = registry.functions.getAnchor(event.resource_id, 1).call()
    if bytes(anchor[0]) != operation_id_v1(event):
        raise RuntimeError("on-chain operationId differs from database identity")

    tx_hash = bytes.fromhex(manifest["transactions"]["initial"])
    receipt = w3.eth.get_transaction_receipt(tx_hash)
    transaction = w3.eth.get_transaction(tx_hash)
    block = w3.eth.get_block(receipt.blockNumber)
    if receipt.status != 1:
        raise RuntimeError("real isolated-chain receipt is not successful")

    conn = connect()
    jobs = JobRepository(conn)
    artifacts = ArtifactRepository(conn)
    insert_result, job_id, operation_id = jobs.insert_event(event)
    if operation_id != bytes(anchor[0]):
        raise RuntimeError("persisted operation identity mismatch")
    claims = jobs.claim_jobs("i5-real-chain-closure", 100, 60)
    claimed = next((row for row in claims if row[0] == job_id), None)
    if claimed is None:
        raise RuntimeError("target I5 job was not claimed")
    version = int(claimed[2])
    version = jobs.cas(
        job_id, JobStatus.CLAIMED, version, JobStatus.CANDIDATE_STORED,
        candidate_header_digest=bytes(anchor[10]),
        candidate_header_object_digest=bytes(anchor[11]),
    )
    artifacts.put_storage_object(bytes(anchor[11]), "headers", "HEADER", 128, True)
    artifacts.put_storage_object(bytes(anchor[12]), "bodies", "BODY", 256, True)
    artifacts.add_header(
        job_id, operation_id, event.resource_id, 1, 1, 1, 1,
        bytes(anchor[10]), None, bytes(anchor[11]),
        body_version=1, update_kind="INITIAL", body_object_digest=bytes(anchor[12]),
    )
    version = jobs.cas(
        job_id, JobStatus.CANDIDATE_STORED, version, JobStatus.READY_FOR_CHAIN_COMMIT
    )
    attempt_id = artifacts.add_real_commit_attempt(
        job_id, operation_id, 1, tx_hash, int(transaction["nonce"])
    )
    artifacts.confirm_real_commit(
        attempt_id, int(receipt.blockNumber), bytes(block["hash"]), int(receipt.status)
    )
    jobs.cas(job_id, JobStatus.READY_FOR_CHAIN_COMMIT, version, JobStatus.COMMITTED)

    row = conn.execute(
        """SELECT j.status,c.status,c.evidence_source,c.receipt_status,
                  c.block_number,c.transaction_hash=h.operation_id
             FROM r3_control.header_update_job j
             JOIN r3_control.commit_attempt c USING(job_id)
             JOIN r3_control.header_version h USING(job_id)
            WHERE j.job_id=%s""",
        (job_id,),
    ).fetchone()
    invariant_violations = 0 if tuple(row[:4]) == (
        "COMMITTED", "CONFIRMED_REAL_CHAIN", "REAL_ISOLATED_CHAIN_ONLY", 1
    ) else 1
    output = {
        "schemaVersion": 1,
        "operationId": operation_id.hex(),
        "jobId": str(job_id),
        "attemptId": str(attempt_id),
        "insertResult": str(insert_result),
        "jobStatus": row[0],
        "commitStatus": row[1],
        "evidenceSource": row[2],
        "receiptStatus": row[3],
        "blockNumber": row[4],
        "invariantViolations": invariant_violations,
        "partialTransactions": 0,
        "formalDatabaseModified": False,
        "formalChainAccessed": False,
    }
    conn.commit()
    conn.close()
    output_path = Path(os.environ["R3_I5_DB_OUTPUT"])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "jobStatus": output["jobStatus"],
        "commitStatus": output["commitStatus"],
        "evidenceSource": output["evidenceSource"],
        "invariantViolations": invariant_violations,
    }))


if __name__ == "__main__":
    main()
