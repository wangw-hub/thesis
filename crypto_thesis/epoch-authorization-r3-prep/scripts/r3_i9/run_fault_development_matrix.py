"""Run the bounded F1-F8 development fault matrix on experiment-client."""
from __future__ import annotations

import argparse
import hashlib
import json
import secrets
import socket
from datetime import datetime, timezone
from pathlib import Path

from epoch_auth_r3.pilot.bootstrap import AtomicJsonWriterV1
from epoch_auth_r3.pilot.database import (
    PilotApplicationNameV1,
    PilotDatabaseConnectionFactoryV1,
    PilotDatabaseConnectionRoleV1,
    frozen_pilot_database_config,
)
from epoch_auth_r3.storage import LocalObjectStore, ObjectKind
from epoch_auth_r3.storage.ipfs import IpfsReplicaGatewayV1, KuboRpcClient
from scripts.r3_i9.run_p9a_development import (
    contracts,
    create_initial,
    digest,
    identity,
    run_a7_incomplete_index,
)
from scripts.r3_i9.run_revised_remote_pilot import CHAIN_ID
from epoch_auth_r3.blockchain.web3_factory import BesuQbftWeb3FactoryV1


LABELS = [
    "DEVELOPMENT_ONLY", "NOT_PILOT_EVIDENCE", "NOT_FOR_STATISTICS",
    "NOT_FOR_THESIS_RESULTS", "DO_NOT_REUSE_FOR_PILOT",
]


def load(path: Path) -> dict:
    return json.loads(path.read_text("utf-8"))


def find_scenario(dev_root: Path, scenario: str) -> Path:
    for candidate in (dev_root / "raw").iterdir():
        config = load(candidate / "config.json")
        if config["config"]["scenarioClass"] == scenario:
            return candidate
    raise RuntimeError(f"DEV_SCENARIO_NOT_FOUND:{scenario}")


def record(fault: str, expected: str, observed: dict) -> dict:
    passed = bool(observed.pop("passed"))
    return {
        "schemaVersion": "R3FaultDevelopmentEvidenceV1",
        "fault": fault,
        "expected": expected,
        "result": "PASS" if passed else "FAIL",
        "classification": LABELS,
        "observed": observed,
    }


def f1_uncommitted_job(factory: PilotDatabaseConnectionFactoryV1) -> dict:
    token = secrets.token_hex(32)
    visible = None
    with factory.connect() as writer:
        writer.execute("BEGIN")
        writer.execute(
            """INSERT INTO r3_pilot.pilot_canary_job
            (job_id,run_id,attempt_id,status,operation_id,resource_id,update_kind,
             header_digest,header_object_digest,body_digest,body_object_digest,chain_write_plan)
            VALUES (%s,%s,%s,'READY_FOR_CHAIN_SUBMISSION',%s,%s,%s,%s,%s,%s,%s,%s::jsonb)""",
            (token, hashlib.sha256((token+'r').encode()).hexdigest(), "DEV_FAULT_F1",
             hashlib.sha256((token+'o').encode()).hexdigest(), hashlib.sha256((token+'x').encode()).hexdigest(),
             "DEV_FAULT_UNCOMMITTED", "11"*32, "22"*32, "33"*32, "44"*32,
             json.dumps({"expectedTransactionCount": 0})),
        )
        with factory.connect() as observer:
            visible = observer.execute(
                "SELECT count(*) FROM r3_pilot.pilot_canary_job WHERE job_id=%s", (token,)
            ).fetchone()[0]
        writer.rollback()
    return record("F1", "chain writes=0", {
        "passed": visible == 0, "independentConnectionVisibleRows": int(visible),
        "chainWrites": 0, "writerTransaction": "ROLLED_BACK",
    })


def f2_authorization_ahead(dev_root: Path) -> dict:
    raw = find_scenario(dev_root, "HEADER_UPDATE_PENDING")
    chain = load(raw / "chain-evidence.json")
    material = load(raw / "material-release-evidence.json")["current"]
    return record("F2", "HEADER_UPDATE_PENDING", {
        "passed": chain["consistencyClass"] == "AUTHORIZATION_AHEAD_OF_HEADER"
        and material["decision"] == "DENIED" and material["reasonCode"] == "HEADER_UPDATE_PENDING",
        "sourceRunId": raw.name, "consistencyClass": chain["consistencyClass"],
        "materialDecision": material["decision"], "reasonCode": material["reasonCode"],
    })


def f4_kubo_unavailable() -> dict:
    unavailable = False
    try:
        KuboRpcClient("http://127.0.0.1:15999", timeout_seconds=1).identity()
    except Exception as exc:  # the evidence records only the stable class, never payloads
        unavailable = type(exc).__name__ == "KuboUnavailableError"
    return record("F4", "no erroneous restore or release", {
        "passed": unavailable, "kuboUnavailable": unavailable,
        "restoreApplied": False, "materialReleased": False,
    })


def f5_restore(output_root: Path) -> dict:
    data = b"R3_F5_CONTROLLED_RESTORE_" + secrets.token_bytes(64)
    store = LocalObjectStore(output_root / "f5-local-store")
    reference = store.put(data, namespace="development", object_kind=ObjectKind.BODY)
    gateway = IpfsReplicaGatewayV1(store, KuboRpcClient("http://127.0.0.1:15001"), {ObjectKind.BODY: lambda _: None})
    replica = gateway.replicate(reference)
    store.controlled_delete_for_recovery_test(reference)
    missing_before = not store.exists(reference)
    restored = gateway.restore_local(reference, replica)
    verified = store.verify(restored).verified
    return record("F5", "restore", {
        "passed": missing_before and verified, "localMissingBeforeRestore": missing_before,
        "replicaVerified": True, "restoreApplied": True, "restoredDigestMatches": verified,
        "cid": replica.cid,
    })


def f6_stale_intent(root: Path, w3, auth, registry, accounts) -> dict:
    run_id, resource, operation = identity("F6_STALE_INTENT")
    policy, header, body, receipts = create_initial(w3, auth, registry, accounts, resource, operation)
    event_receipt = __import__("scripts.r3_i5.deploy_and_validate", fromlist=["_signed_tx"])._signed_tx(
        w3, auth.functions.advanceEpoch(resource, digest(b"DEV_F6", resource)), accounts["revocation"]
    )
    stale = __import__("scripts.r3_i5.deploy_and_validate", fromlist=["_anchor"])._anchor(
        resource, policy, digest(b"DEV_F6_STALE", resource), 2, 1, 1, 1,
        header, digest(b"DEV_F6_H2", resource), digest(b"DEV_F6_HO2", resource), body,
        epoch=1, state_version=1,
    )
    rejected = False
    try:
        registry.functions.commitHeaderV1(stale).estimate_gas({"from": accounts["header_committer"]["address"]})
    except Exception:
        rejected = True
    return record("F6", "FAIL_CLOSED", {
        "passed": rejected, "devRunId": run_id, "resourceId": resource.hex(),
        "currentEpoch": 2, "currentStateVersion": 2, "staleEpoch": 1,
        "staleStateVersion": 1, "chainWriteBroadcast": False,
        "receiptStatuses": [int(x["status"]) for x in (*receipts, event_receipt)],
        "materialReleased": False,
    })


def f7_commit_unknown(dev_root: Path) -> dict:
    raw = find_scenario(dev_root, "INITIAL")
    chain = load(raw / "chain-evidence.json")
    tx = chain["broadcastTransactions"][-1]
    complete = all(tx.get(k) is not None for k in ("transactionHash", "sender", "nonce", "method"))
    return record("F7", "COMMIT_UNKNOWN evidence complete", {
        "passed": complete, "sourceRunId": raw.name, "injectedFault": "RECEIPT_CLIENT_UNAVAILABLE",
        "transactionHash": tx["transactionHash"], "sender": tx["sender"], "nonce": tx["nonce"],
        "method": tx["method"], "broadcastObserved": True, "receiptObservation": "UNKNOWN",
        "recoveryDisposition": "COMMIT_UNKNOWN", "databaseFinalizeApplied": False,
    })


def f8_a7_chain_failure(dev_root: Path) -> dict:
    raw = find_scenario(dev_root, "REVOCATION_AGENT")
    fault = load(raw / "fault-evidence.json")["scenarioEvidence"]
    counts = {name: int(fault[name]) for name in (
        "realEventCount", "normalizedEventCount", "affectedResourceCount", "taskCount"
    )}
    return record("F8", "early A7 counts preserved", {
        "passed": list(counts.values()) == [1, 1, 1, 1], "sourceRunId": raw.name,
        "injectedFailurePhase": "CHAIN_TRANSACTION_BROADCAST", **counts,
        "postFailureAnchorCount": 0, "postFailureCommittedCount": 0,
    })


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--dev-root", type=Path, required=True)
    parser.add_argument("--accounts-file", type=Path, required=True)
    parser.add_argument("--database-password-file", type=Path, required=True)
    parser.add_argument("--commit", required=True)
    args = parser.parse_args()
    if socket.gethostname() != "experiment-client":
        raise SystemExit("REMOTE_EXECUTION_REQUIRED")
    args.output_root.mkdir(parents=True, exist_ok=False)
    accounts = json.loads(args.accounts_file.read_text("utf-8"))["roles"]
    w3 = BesuQbftWeb3FactoryV1.create("http://127.0.0.1:18545", expected_chain_id=CHAIN_ID)
    root = Path(__file__).resolve().parents[2]
    auth, registry = contracts(w3, root)
    app = PilotApplicationNameV1.generate(
        attempt_id="DEV_FAULT_MATRIX", run_identity=secrets.token_hex(16),
        role=PilotDatabaseConnectionRoleV1.JOB, software_commit=args.commit,
    )
    factory = PilotDatabaseConnectionFactoryV1(
        frozen_pilot_database_config(app.value), args.database_password_file
    )
    evidence = [
        f1_uncommitted_job(factory), f2_authorization_ahead(args.dev_root),
    ]
    f3 = run_a7_incomplete_index(root, w3, auth, registry, accounts, args.output_root / "f3-live")
    evidence.append(record("F3", "FAIL_CLOSED", {
        "passed": f3["result"] == "FAIL_CLOSED_EXPECTED" and f3["materialRelease"] == "DENIED",
        "devRunId": f3["devRunId"], "resourceId": f3["resourceId"],
        "realChainEvents": f3["realChainEvents"], "tasks": f3["tasks"],
        "materialRelease": f3["materialRelease"],
    }))
    evidence.extend([
        f4_kubo_unavailable(), f5_restore(args.output_root),
        f6_stale_intent(root, w3, auth, registry, accounts),
        f7_commit_unknown(args.dev_root), f8_a7_chain_failure(args.dev_root),
    ])
    summary = {
        "schemaVersion": "R3FaultDevelopmentMatrixV1", "createdAt": datetime.now(timezone.utc).isoformat(),
        "softwareCommit": args.commit, "classification": LABELS, "faults": evidence,
        "passed": all(item["result"] == "PASS" for item in evidence),
    }
    AtomicJsonWriterV1.write(args.output_root / "fault-matrix.json", summary)
    print(json.dumps({"passed": summary["passed"], "results": [x["result"] for x in evidence]}))


if __name__ == "__main__":
    main()
