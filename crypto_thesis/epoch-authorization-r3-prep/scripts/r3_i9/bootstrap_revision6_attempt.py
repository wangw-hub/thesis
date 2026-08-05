from __future__ import annotations
import argparse, hashlib, json, os, socket
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from epoch_auth_r3.blockchain import CompositeReadStatus, CompositeStateGateway
from epoch_auth_r3.blockchain.web3_factory import BesuQbftWeb3FactoryV1
from epoch_auth_r3.pilot.bootstrap import AtomicJsonWriterV1, AttemptBootstrapLockV1, AttemptBootstrapManifestV1, BootstrapState
from epoch_auth_r3.pilot.attempt import PilotAttemptIdV1
from epoch_auth_r3.pilot.database import (
    PilotApplicationNameV1, PilotDatabaseConnectionFactoryV1,
    PilotDatabaseConnectionRoleV1, frozen_pilot_database_config,
)
from epoch_auth_r3.pilot.phase_contract import contract_for
from scripts.r3_i9.run_revised_remote_pilot import AUTH, AUTH_ABI, CHAIN_ID, REGISTRY

def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(",",":"),default=str).encode()).hexdigest()

def main() -> None:
    p=argparse.ArgumentParser(); p.add_argument("--attempt-id",required=True); p.add_argument("--commit",required=True); p.add_argument("--archive-sha",required=True); p.add_argument("--password-file",required=True); p.add_argument("--preflight-resource",required=True); p.add_argument("--preflight-tx",required=True); p.add_argument("--purpose",choices=("ONE_CANARY_ONLY","P9_A_SMOKE_ONLY"),default="ONE_CANARY_ONLY"); a=p.parse_args()
    if socket.gethostname()!="experiment-client": raise SystemExit("REMOTE_EXECUTION_REQUIRED")
    a.attempt_id=PilotAttemptIdV1.validate(a.attempt_id).serialize()
    base=Path("/var/lib/epoch-auth-r3/i9-pilot/attempts"); final=base/a.attempt_id; staging=base/f".staging-{a.attempt_id}"
    if final.exists() or staging.exists(): raise SystemExit("ATTEMPT_ALREADY_EXISTS")
    lock=base/".locks"/f"{a.attempt_id}.lock"
    with AttemptBootstrapLockV1(lock,a.attempt_id,a.commit):
        staging.mkdir(parents=True); [ (staging/name).mkdir() for name in ("configs","workloads","raw","logs","state","manifests","invalid-runs","runtime","local-store") ]
        app_name=PilotApplicationNameV1.generate(
            attempt_id=a.attempt_id, run_identity="NO_RUN",
            role=PilotDatabaseConnectionRoleV1.BOOTSTRAP, software_commit=a.commit)
        db_config=frozen_pilot_database_config(app_name.value); db_factory=PilotDatabaseConnectionFactoryV1(db_config,Path(a.password_file)); db_attestation=db_factory.attest()
        w3=BesuQbftWeb3FactoryV1.create("http://127.0.0.1:18545",expected_chain_id=CHAIN_ID)
        latest=int(w3.eth.block_number); block=w3.eth.get_block(latest); fixed=w3.eth.get_block(latest)
        if bytes(block["hash"])!=bytes(fixed["hash"]): raise RuntimeError("LATEST_FIXED_BLOCK_HASH_MISMATCH")
        receipt=w3.eth.get_transaction_receipt(a.preflight_tx); logs=w3.eth.get_logs({"fromBlock":int(receipt["blockNumber"]),"toBlock":int(receipt["blockNumber"])})
        registry_abi=json.loads((Path(__file__).resolve().parents[2]/"contracts/r3/build/HeaderRegistryV1.json").read_text())["abi"]
        auth=w3.eth.contract(address=AUTH,abi=AUTH_ABI); registry=w3.eth.contract(address=REGISTRY,abi=registry_abi)
        composite=CompositeStateGateway(w3,auth,registry).read(bytes.fromhex(a.preflight_resource),block_identifier=latest)
        if composite.status is not CompositeReadStatus.CONFIRMED: raise RuntimeError("COMPOSITE_PREFLIGHT_FAILED")
        web3_attestation={"chainId":int(w3.eth.chain_id),"clientVersion":w3.client_version,"latestResolvedBlockNumber":latest,"latestResolvedBlockHash":bytes(fixed["hash"]).hex(),"receiptBlock":int(receipt["blockNumber"]),"receiptStatus":int(receipt["status"]),"logCount":len(logs),"compositeBlock":composite.block_number,"extraDataLengthErrors":0,"recoverySnapshotReadOnly":True}
        p9a = a.purpose == "P9_A_SMOKE_ONLY"
        stage_gate={
            "schemaVersion":1,
            "attemptId":a.attempt_id,
            "canary":"CANARY_PASSED" if p9a else "NOT_STARTED",
            "state":"P9_A_READY" if p9a else "P9_A_NOT_STARTED",
            "history":[{
                "stage":"P9-A",
                "transition":"P9_A_APPROVED_BY_USER",
                "at":datetime.now(timezone.utc).isoformat(),
            }] if p9a else [],
            "p9BTasksCreated":False,
        }
        environment={"executionHost":"experiment-client","remoteAttemptRoot":str(final),"chainId":CHAIN_ID,"formalSystemsAccessed":False}
        contract=contract_for("CANARY_INITIAL_END_TO_END")
        values={"database-config.json":db_config.redacted_dict(),"database-attestation.json":db_attestation,"web3-attestation.json":web3_attestation,"environment.json":environment,"phase-contract.json":contract,"stage-gate-state.json":stage_gate,"old-run-ids.json":[]}
        for name,value in values.items(): AtomicJsonWriterV1.write(staging/("state" if name=="stage-gate-state.json" else "manifests")/name,value)
        manifest=AttemptBootstrapManifestV1(1,a.attempt_id,a.purpose,a.commit,a.archive_sha,digest(environment),digest(db_config.redacted_dict()),digest(db_attestation),digest({"rpc":"127.0.0.1:18545"}),digest(web3_attestation),digest(contract),digest(stage_gate),"experiment-client",str(final),datetime.now(timezone.utc).isoformat(),BootstrapState.PLANNED.value)
        for state in (BootstrapState.STAGING_CREATED,BootstrapState.CONFIG_WRITTEN,BootstrapState.CONFIG_VALIDATED,BootstrapState.DATABASE_ATTESTED,BootstrapState.WEB3_ATTESTED,BootstrapState.PREFLIGHT_COMPLETED,BootstrapState.READY_FOR_CANARY): manifest=manifest.transition(state)
        AtomicJsonWriterV1.write(staging/"manifests/attempt-bootstrap-manifest.json",asdict(manifest))
        os.replace(staging,final)
        manifest=manifest.transition(BootstrapState.PUBLISHED); AtomicJsonWriterV1.write(final/"manifests/attempt-bootstrap-manifest.json",asdict(manifest))
        print(json.dumps({"attemptId":a.attempt_id,"bootstrapState":manifest.bootstrapState,"database":db_attestation,"web3":web3_attestation},sort_keys=True))
if __name__=="__main__": main()
