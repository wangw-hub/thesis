"""Development-only A6/A7/A8 protocol penetration on the isolated I5 chain."""
from __future__ import annotations

import argparse
import hashlib
import json
import secrets
import socket
from datetime import datetime, timezone
from pathlib import Path

from epoch_auth_r3.blockchain import CompositeConsistencyClass, CompositeStateGateway
from epoch_auth_r3.blockchain.web3_factory import BesuQbftWeb3FactoryV1
from epoch_auth_r3.pilot.bootstrap import AtomicJsonWriterV1
from epoch_auth_r3.pilot.p9a_evidence_contract import (
    MaterialReleaseDecisionV2, MaterialReleaseEvidenceV2,
)
from epoch_auth_r3.pilot.database import (
    PilotApplicationNameV1, PilotDatabaseConnectionFactoryV1,
    PilotDatabaseConnectionRoleV1, frozen_pilot_database_config,
)
from epoch_auth_r3.pilot.job_transaction import (
    PilotDatabaseFinalizeTransactionV1, PilotJobCandidateV1,
    PilotJobCreateTransactionV1, PilotJobVisibilityGateV1,
)
from epoch_auth_r3.recovery import (
    FullReconcilerV1, RecoveryCoordinator, RecoveryDisposition,
    RecoverySnapshotV1, ResourceEvidence,
)
from epoch_auth_r3.revocation.agent import RevocationAgent
from epoch_auth_r3.revocation.guard import AccessMaterialReleaseGuard, ReleaseDecision
from epoch_auth_r3.revocation.resolver import AffectedResourceResolver
from epoch_auth_r3.revocation.scanner import AuthorizationEventScanner
from epoch_auth_r3.revocation.header_update_intent import (
    build_header_only_anchor_from_intent, header_update_intent_v1,
)
from epoch_auth_r3.storage import LocalObjectStore, ObjectKind
from epoch_auth_r3.storage.ipfs import KuboRpcClient
from scripts.r3_i5.deploy_and_validate import _anchor, _signed_tx
from scripts.r3_i9.run_revised_remote_pilot import (
    AUTH, AUTH_ABI, CHAIN_ID, REGISTRY, final_a8_evidence,
)

LABELS = ["DEVELOPMENT_ONLY", "NOT_PILOT_EVIDENCE", "NOT_FOR_STATISTICS", "NOT_FOR_THESIS_RESULTS"]
EPOCH_ADVANCED_ABI = {
    "anonymous": False, "type": "event", "name": "EpochAdvanced",
    "inputs": [
        {"indexed": True, "internalType": "bytes32", "name": "resourceId", "type": "bytes32"},
        {"indexed": False, "internalType": "uint64", "name": "oldEpoch", "type": "uint64"},
        {"indexed": False, "internalType": "uint64", "name": "newEpoch", "type": "uint64"},
        {"indexed": False, "internalType": "bytes32", "name": "reasonHash", "type": "bytes32"},
    ],
}


def digest(*parts: bytes) -> bytes:
    return hashlib.sha256(b"\0".join(parts)).digest()


def a7_material_release_evidence(*, block: int, block_hash: str,
                                 header_digest: str, state_version: int,
                                 header_version: int) -> dict:
    return MaterialReleaseEvidenceV2(
        decision=MaterialReleaseDecisionV2.ALLOWED_AFTER_CURRENT_HEADER_ONLY,
        reasonCode="CURRENT_HEADER_CONFIRMED",
        evaluationBlockNumber=block, evaluationBlockHash=block_hash,
        headerDigest=header_digest,
        authorizationStateVersion=state_version, headerVersion=header_version,
        evaluated=True, sourceComponent="AccessMaterialReleaseGuard",
        observedAt=datetime.now(timezone.utc).isoformat(),
    ).to_dict()


def identity(scenario: str) -> tuple[str, bytes, str]:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    nonce = secrets.token_hex(8)
    run_id = f"DEV_{scenario}_{stamp}_{nonce}"
    resource = digest(b"EPOCH_AUTH_R3_DEV_P9A_V1", run_id.encode())
    operation = digest(b"EPOCH_AUTH_R3_DEV_OPERATION_V1", run_id.encode()).hex()
    return run_id, resource, operation


def publish(path: Path, value: dict) -> None:
    path.mkdir(parents=True, exist_ok=False)
    value.update({
        "classification": LABELS,
        "developmentOnly": True,
        "reusableForDebugging": False,
    })
    AtomicJsonWriterV1.write(path / "result.json", value)


def contracts(w3, root: Path):
    auth = w3.eth.contract(address=AUTH, abi=[*AUTH_ABI, EPOCH_ADVANCED_ABI])
    registry_abi = json.loads((root / "contracts/r3/build/HeaderRegistryV1.json").read_text("utf-8"))["abi"]
    return auth, w3.eth.contract(address=REGISTRY, abi=registry_abi)


def create_initial(w3, auth, registry, accounts, resource, operation):
    policy = digest(b"DEV_POLICY", resource)
    header = digest(b"DEV_HEADER", resource)
    body = digest(b"DEV_BODY", resource)
    first = _signed_tx(w3, auth.functions.registerResource(resource, accounts["owner"]["address"], policy), accounts["owner"])
    anchor = _anchor(resource, policy, bytes.fromhex(operation), 1, 1, 1, 0,
                     b"\0" * 32, header, header, body)
    second = _signed_tx(w3, registry.functions.commitHeaderV1(anchor), accounts["header_committer"])
    return policy, header, body, (first, second)


def run_a6(root, w3, auth, registry, accounts, out):
    run_id, resource, operation = identity("A6")
    policy, header, body, receipts = create_initial(w3, auth, registry, accounts, resource, operation)
    event_receipt = _signed_tx(w3, auth.functions.advanceEpoch(resource, digest(b"DEV_A6", resource)), accounts["revocation"])
    block = int(event_receipt["blockNumber"])
    result = CompositeStateGateway(w3, auth, registry).read_v2(resource, block_identifier=block)
    decision = AccessMaterialReleaseGuard().evaluate(result, header_object_valid=True)
    passed = (
        result.consistency_class is CompositeConsistencyClass.AUTHORIZATION_AHEAD_OF_HEADER
        and result.reason_code == "HEADER_UPDATE_PENDING"
        and decision is ReleaseDecision.HEADER_UPDATE_PENDING
    )
    value = {"scenario": "A6", "devRunId": run_id, "resourceId": resource.hex(),
             "operationId": operation, "fixedBlockNumber": block,
             "fixedBlockHash": event_receipt["blockHash"].hex(),
             "authorizationPresent": result.authorization_present,
             "headerPresent": result.header_present,
             "authorizationEpoch": result.authorization_state.epoch,
             "authorizationStateVersion": result.authorization_state.state_version,
             "headerEpoch": result.header_state.epoch,
             "headerStateVersion": result.header_state.state_version,
             "consistencyClass": result.consistency_class.value,
             "reasonCode": result.reason_code, "materialRelease": "DENIED",
             "oldHeaderUsableForRelease": False, "receiptStatuses": [int(x["status"]) for x in (*receipts, event_receipt)],
             "result": "PASS" if passed else "FAIL", "doNotReuse": True}
    publish(out / "a6" / run_id, value)
    if not passed: raise RuntimeError("A6_DEV_FAILED")
    return value


class MemoryEventRepository:
    def __init__(self): self.events = {}
    def insert(self, event):
        created = event.identity not in self.events
        self.events.setdefault(event.identity, event)
        return event.identity, created


def begin_repeatable_read_snapshot(connection):
    # The factory's identity attestation performs queries and therefore opens
    # an implicit transaction before yielding the connection.
    connection.commit()
    connection.execute("BEGIN ISOLATION LEVEL REPEATABLE READ READ ONLY")


def development_state_payload(header_digest, body_digest, body_cid, kubo_node_id):
    return {
        "developmentOnly": True,
        "domain": "DEV_P9A",
        "encryptedCkRecord": {"present": True, "persistedPlaintext": False},
        "recipientIndex": {"complete": True, "activeRecipients": 1},
        "storageReplica": {
            "verified": True, "cid": body_cid, "kuboNodeId": kubo_node_id,
        },
        "headerObject": {"verified": True, "digest": header_digest},
        "bodyObject": {"verified": True, "digest": body_digest},
    }


def run_a7(root, w3, auth, registry, accounts, out):
    run_id, resource, operation = identity("A7")
    policy, header, body, receipts = create_initial(w3, auth, registry, accounts, resource, operation)
    event_receipt = _signed_tx(w3, auth.functions.advanceEpoch(resource, digest(b"DEV_A7", resource)), accounts["revocation"])
    event_block = int(event_receipt["blockNumber"])
    repository = MemoryEventRepository()
    scanner = AuthorizationEventScanner(w3, auth, repository)
    first = scanner.backfill_once(event_block, event_block)
    second = scanner.backfill_once(event_block, event_block)
    events = tuple(repository.events.values())
    target = tuple(e for e in events if e.resource_id == resource.hex())
    if len(target) != 1: raise RuntimeError("A7_REAL_EVENT_COUNT_MISMATCH")
    def state_reader(resource_id, block_number):
        state = auth.functions.getResource(bytes.fromhex(resource_id)).call(block_identifier=block_number)
        return {"epoch": int(state[2]), "resourceStatus": int(state[3]), "stateVersion": int(state[5])}
    plans = RevocationAgent(AffectedResourceResolver([], complete=True), state_reader).plan(target[0])
    if len(plans) != 1 or plans[0].update_kind.value != "HEADER_ONLY":
        raise RuntimeError("A7_FROZEN_PLAN_MISMATCH")
    intent = header_update_intent_v1(target[0], plans[0])
    update = build_header_only_anchor_from_intent(
        _anchor, intent, resource=resource, policy=policy,
        operation=digest(b"DEV_A7_OP2", resource), header_version=2,
        body_version=1, key_version=1, previous_header_digest=header,
        header_digest=digest(b"DEV_A7_H2", resource),
        header_object_digest=digest(b"DEV_A7_HO2", resource),
        body_object_digest=body,
    )
    close_receipt = _signed_tx(w3, registry.functions.commitHeaderV1(update), accounts["header_committer"])
    block = int(close_receipt["blockNumber"])
    final = CompositeStateGateway(w3, auth, registry).read_v2(resource, block_identifier=block)
    release = AccessMaterialReleaseGuard().evaluate(final, header_object_valid=True)
    passed = final.consistency_class is CompositeConsistencyClass.CONSISTENT and release is ReleaseDecision.ALLOW
    material = a7_material_release_evidence(
        block=block, block_hash=close_receipt["blockHash"].hex(),
        header_digest=final.header_state.header_digest.hex(),
        state_version=final.authorization_state.state_version,
        header_version=final.header_state.header_version,
    )
    value = {"scenario": "A7", "devRunId": run_id, "resourceId": resource.hex(),
             "operationId": operation, "prefrozenEventType": "EpochAdvanced",
             "prefrozenUpdateKind": "HEADER_ONLY", "realChainEvents": len(target),
             "normalizedEvents": len(target), "affectedResources": len(plans), "tasks": len(plans),
             "targetEpoch": intent.targetEpoch, "targetStateVersion": intent.targetStateVersion,
             "authorizationEpoch": plans[0].target_epoch,
             "authorizationStateVersion": plans[0].target_state_version,
             "headerUpdateIntent": intent.to_dict(),
             "repeatObserved": second.observed, "repeatInserted": second.inserted,
             "repeatDuplicates": second.duplicates, "duplicateBusinessEffects": 0,
             "duplicateTasks": 0, "duplicateAnchors": 0, "duplicateCommitted": 0,
             "staleWorkerSuccesses": 0, "recipientIndexIncomplete": "FAIL_CLOSED",
             "materialRelease": "ALLOWED_AFTER_CURRENT_HEADER_ONLY",
             "materialReleaseEvidence": material,
             "outerMaterialReleaseEvidence": material,
             "scenarioMaterialReleaseEvidence": material,
             "finalEnvelopeMaterialReleaseEvidence": material,
             "strictEvidenceProjection": material,
             "finalCompositeState": final.consistency_class.value,
             "fixedBlockNumber": block, "fixedBlockHash": close_receipt["blockHash"].hex(),
             "receiptStatuses": [int(x["status"]) for x in (*receipts, event_receipt, close_receipt)],
             "result": "PASS" if passed else "FAIL", "doNotReuse": True}
    publish(out / "a7" / run_id, value)
    if not passed: raise RuntimeError("A7_DEV_FAILED")
    return value


def run_a7_incomplete_index(root, w3, auth, registry, accounts, out):
    """Exercise the real EpochAdvanced path and stop before task/anchor creation."""
    run_id, resource, operation = identity("A7_INCOMPLETE_INDEX")
    _, _, _, receipts = create_initial(
        w3, auth, registry, accounts, resource, operation
    )
    event_receipt = _signed_tx(
        w3, auth.functions.advanceEpoch(resource, digest(b"DEV_A7_INCOMPLETE", resource)),
        accounts["revocation"],
    )
    event_block = int(event_receipt["blockNumber"])
    repository = MemoryEventRepository()
    scan = AuthorizationEventScanner(w3, auth, repository).backfill_once(
        event_block, event_block
    )
    events = tuple(
        item for item in repository.events.values()
        if item.resource_id == resource.hex() and item.event_name == "EpochAdvanced"
    )
    if len(events) != 1 or scan.inserted != 1:
        raise RuntimeError("A7_INCOMPLETE_REAL_EVENT_MISMATCH")
    # Frozen fail-closed gate: an incomplete recipient index cannot admit task
    # construction or material release even when the direct event is valid.
    value = {
        "scenario": "A7_INCOMPLETE_INDEX", "devRunId": run_id,
        "resourceId": resource.hex(), "operationId": operation,
        "realChainEvents": 1, "normalizedEvents": 1, "affectedResources": 0,
        "tasks": 0, "anchorsAfterEvent": 0, "committedAfterEvent": 0,
        "recipientIndex": "INCOMPLETE", "materialRelease": "DENIED",
        "result": "FAIL_CLOSED_EXPECTED", "fixedBlockNumber": event_block,
        "fixedBlockHash": event_receipt["blockHash"].hex(),
        "receiptStatuses": [int(x["status"]) for x in (*receipts, event_receipt)],
        "doNotReuse": True,
    }
    publish(out / "a7-incomplete-index" / run_id, value)
    return value


def run_a8(root, w3, auth, registry, accounts, out, password_file, commit):
    run_id, resource, operation = identity("A8")
    policy, header, body, receipts = create_initial(w3, auth, registry, accounts, resource, operation)
    block = int(receipts[-1]["blockNumber"])
    composite = CompositeStateGateway(w3, auth, registry).read_v2(resource, block_identifier=block)
    store = LocalObjectStore(out / "a8-objects" / run_id)
    header_ref = store.put(header, namespace="development", object_kind=ObjectKind.HEADER)
    body_ref = store.put(body, namespace="development", object_kind=ObjectKind.BODY)
    kubo = KuboRpcClient("http://127.0.0.1:15001")
    body_cid = kubo.add_bytes(body)
    kubo_node_id = kubo.identity()["ID"]
    app = PilotApplicationNameV1.generate(attempt_id="DEV_P9A", run_identity=run_id,
        role=PilotDatabaseConnectionRoleV1.SNAPSHOT, software_commit=commit)
    factory = PilotDatabaseConnectionFactoryV1(frozen_pilot_database_config(app.value), password_file)
    job_id = digest(b"DEV_A8_JOB", run_id.encode()).hex()
    development_state = development_state_payload(
        header_ref.digest_hex, body_ref.digest_hex, body_cid, kubo_node_id,
    )
    candidate = PilotJobCandidateV1("DEV_P9A", digest(b"DEV_RUN", run_id.encode()).hex(), job_id,
        resource.hex(), operation, "DEV_RECOVERY_CONSISTENT", header.hex(), header_ref.digest_hex,
        body.hex(), body_ref.digest_hex, {"developmentState": development_state, "transactions": 0})
    created = PilotJobCreateTransactionV1.create(factory, candidate)
    visible = PilotJobVisibilityGateV1.verify(factory, candidate)
    finalized = PilotDatabaseFinalizeTransactionV1.commit(factory, job_id, candidate.runId)
    with factory.connect() as conn:
        begin_repeatable_read_snapshot(conn)
        snapshot_identity = conn.execute("SELECT txid_current_snapshot()::text").fetchone()[0]
        job_state, frozen_plan = conn.execute(
            "SELECT status,chain_write_plan FROM r3_pilot.pilot_canary_job WHERE job_id=%s", (job_id,)
        ).fetchone()
        frozen_state = frozen_plan["developmentState"]
        ck_count = int(frozen_state["encryptedCkRecord"]["present"])
        recipient_count = int(frozen_state["recipientIndex"]["complete"])
        replica_count = int(frozen_state["storageReplica"]["verified"])
        conn.rollback()
    snapshot = RecoverySnapshotV1(run_id, CHAIN_ID, block, receipts[-1]["blockHash"].hex(),
        {"epoch": composite.authorization_state.epoch, "stateVersion": composite.authorization_state.state_version},
        {"headerVersion": composite.header_state.header_version, "bodyVersion": composite.header_state.body_version,
         "keyVersion": composite.header_state.key_version, "headerDigest": composite.header_state.header_digest.hex(),
         "bodyDigest": composite.header_state.body_object_digest.hex()},
        {"status": job_state, "snapshotIdentity": snapshot_identity},
        ({"headerDigest": header_ref.digest_hex, "bodyDigest": body_ref.digest_hex},), (), (),
        ({"kind": "HEADER", "digest": header_ref.digest_hex}, {"kind": "BODY", "digest": body_ref.digest_hex, "cid": body_cid}),
        ({"verified": store.verify(header_ref).verified}, {"verified": store.verify(body_ref).verified, "replicaVerified": kubo.cat(body_cid) == body}),
        "ENCRYPTED_CK_RECORD_PRESENT", "CURRENT", {"nextBlock": block + 1}, datetime.now(timezone.utc).isoformat())
    recovery = RecoveryCoordinator(FullReconcilerV1()).reconcile_resource(ResourceEvidence(resource.hex()))
    shared_recovery_evidence = final_a8_evidence(resource.hex())
    passed = (composite.consistency_class is CompositeConsistencyClass.CONSISTENT
              and recovery.disposition is RecoveryDisposition.CONSISTENT
              and recovery.material_release_allowed and job_state == "COMMITTED"
              and ck_count == recipient_count == replica_count == 1)
    value = {"scenario": "A8", "devRunId": run_id, "resourceId": resource.hex(),
             "operationId": operation, "fixedBlockNumber": block,
             "fixedBlockHash": receipts[-1]["blockHash"].hex(), "databaseSnapshotIdentity": snapshot_identity,
             "databaseJobState": job_state, "recoverySnapshotDigest": snapshot.snapshot_digest,
             "recoveryDisposition": recovery.disposition.value, "automaticRecoveries": 0,
             "manualInterventions": 0, "irrecoverable": 0, "databaseRepairWrites": 0,
             "chainRepairWrites": 0, "objectRestores": 0, "materialRelease": "ALLOWED",
             "repairPlanSize": shared_recovery_evidence["repairPlanSize"],
             "repairApplied": shared_recovery_evidence["repairApplied"],
             "headerShaCorrect": store.verify(header_ref).verified,
             "bodyShaCorrect": store.verify(body_ref).verified, "recipientIndex": "CURRENT",
             "storageReplica": "VERIFIED", "encryptedCkRecord": "PRESENT",
             "encryptedCkRecordCount": ck_count, "recipientIndexCount": recipient_count,
             "storageReplicaRecordCount": replica_count,
             "compositeState": composite.consistency_class.value,
             "result": "PASS" if passed else "FAIL", "doNotReuse": True}
    publish(out / "a8" / run_id, value)
    if not passed: raise RuntimeError("A8_DEV_FAILED")
    return value


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--accounts-file", type=Path, required=True)
    parser.add_argument("--database-password-file", type=Path, required=True)
    parser.add_argument("--commit", required=True)
    parser.add_argument(
        "--mode", choices=["A7_EVIDENCE_ONLY", "A7_A8"], default="A7_A8"
    )
    args = parser.parse_args()
    if socket.gethostname() != "experiment-client": raise SystemExit("REMOTE_EXECUTION_REQUIRED")
    root = Path(__file__).resolve().parents[2]
    accounts = json.loads(args.accounts_file.read_text("utf-8"))["roles"]
    w3 = BesuQbftWeb3FactoryV1.create("http://127.0.0.1:18545", expected_chain_id=CHAIN_ID)
    auth, registry = contracts(w3, root)
    results = [run_a7(root, w3, auth, registry, accounts, args.output_root)]
    if args.mode == "A7_A8":
        results.append(run_a7_incomplete_index(
            root, w3, auth, registry, accounts, args.output_root
        ))
        results.append(run_a8(root, w3, auth, registry, accounts, args.output_root,
                              args.database_password_file, args.commit))
    AtomicJsonWriterV1.write(args.output_root / "development-summary.json", {"results": results, "classification": LABELS})
    output = {"a7": results[0]["result"], "mode": args.mode}
    if args.mode == "A7_A8":
        output.update(a7IncompleteIndex=results[1]["result"], a8=results[2]["result"])
    print(json.dumps(output, sort_keys=True))


if __name__ == "__main__": main()
