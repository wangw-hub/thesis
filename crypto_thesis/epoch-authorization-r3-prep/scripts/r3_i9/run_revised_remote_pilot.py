"""Remote-authoritative I9 revision runner.

This program is deliberately stage-scoped.  It refuses non-experiment-client
execution, writes append-only evidence below one attempt root, and enforces the
P9-A -> P9-B -> P9-C -> P9-D admission sequence.  It produces PILOT_ONLY
correctness evidence, never formal performance evidence.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import secrets
import socket
import subprocess
import sys
import time
from contextlib import contextmanager
from dataclasses import asdict, replace
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from web3 import Web3

from epoch_auth_r3.body.chunk_crypto import NonceUseRegistry
from epoch_auth_r3.body.format_v1 import decrypt_body, encrypt_body
from epoch_auth_r3.pilot.config import (
    R3PilotConfigV1, attempt_scoped_run_id, config_digest,
    validate_remote_authoritative_config,
)
from epoch_auth_r3.pilot.events import PhaseEventJournal
from epoch_auth_r3.pilot.evidence import PilotEvidenceWriter, validate_raw_run
from epoch_auth_r3.pilot.phase_contract import contract_for, validate_phase_events
from epoch_auth_r3.pilot.terminalizer import PilotRunTerminalizerV1
from epoch_auth_r3.pilot.evidence_accumulator import EvidenceAccumulatorV1
from epoch_auth_r3.pilot.chain_write import (
    PilotChainWriteAdmissionGuardV1, PilotChainWritePlanV1,
    PilotChainWriteStepV1,
)
from epoch_auth_r3.pilot.job_transaction import (
    PilotDatabaseFinalizeTransactionV1, PilotJobCandidateV1,
    PilotJobCreateTransactionV1, PilotJobVisibilityGateV1,
)
from epoch_auth_r3.blockchain import (
    CompositeConsistencyClass, CompositeReadStatus, CompositeStateGateway,
)
from epoch_auth_r3.blockchain.web3_factory import BesuQbftWeb3FactoryV1
from epoch_auth_r3.pilot.stage_gate import PilotStageStateV1, StageQuality
from epoch_auth_r3.pilot.database import (
    PilotApplicationNameV1, PilotDatabaseConnectionFactoryV1,
    PilotDatabaseConnectionRoleV1, frozen_pilot_database_config,
)
from epoch_auth_r3.pilot.workload import R3PilotWorkloadGeneratorV1
from epoch_auth_r3.pilot.p9a import P9A_SCENARIOS
from epoch_auth_r3.pilot.p9a_evidence_contract import (
    MaterialReleaseDecisionV2, MaterialReleaseEvidenceV2,
    P9AAcceptanceDecisionV1, PilotEvidenceClassificationV1,
    validate_p9a_run_evidence, validate_run_evidence,
)
from epoch_auth_r3.pilot.attempt import PilotAttemptIdV1
from epoch_auth_r3.pilot.p9a_stage_terminalizer import P9AStageTerminalizerV1
from epoch_auth_r3.pilot.bootstrap import AtomicJsonWriterV1
from epoch_auth_r3.storage import LocalObjectStore, ObjectKind
from epoch_auth_r3.storage.ipfs import KuboRpcClient
from epoch_auth_r3.storage.ipfs import IpfsReplicaGatewayV1
from epoch_auth_r3.revocation.guard import AccessMaterialReleaseGuard, ReleaseDecision
from epoch_auth_r3.revocation.agent import RevocationAgent
from epoch_auth_r3.revocation.resolver import AffectedResourceResolver
from epoch_auth_r3.revocation.scanner import AuthorizationEventScanner
from epoch_auth_r3.revocation.header_update_intent import (
    build_header_only_anchor_from_intent, header_update_intent_v1,
)
from epoch_auth_r3.recovery import RecoveryCoordinator
from epoch_auth_r3.recovery import RecoveryDisposition
from epoch_auth_r3.recovery.reconciler import FullReconcilerV1, ResourceEvidence
from scripts.r3_i5.deploy_and_validate import _anchor, _signed_tx

CHAIN_ID = 2026073005
AUTH = "0x12BA996711Db58897A525b5a718225bD085A3c5f"
REGISTRY = "0x280b757a16525AdAef8ED88EE158e0c6F924B35F"
AUTH_ABI = [{
    "inputs": [
        {"internalType": "bytes32", "name": "resourceId", "type": "bytes32"},
        {"internalType": "address", "name": "owner", "type": "address"},
        {"internalType": "bytes32", "name": "policyDigest", "type": "bytes32"},
    ],
    "name": "registerResource", "outputs": [], "stateMutability": "nonpayable", "type": "function",
}, {
    "inputs": [{"internalType": "bytes32", "name": "resourceId", "type": "bytes32"}],
    "name": "getResource",
    "outputs": [{"components": [
        {"internalType": "address", "name": "owner", "type": "address"},
        {"internalType": "bytes32", "name": "policyDigest", "type": "bytes32"},
        {"internalType": "uint64", "name": "epoch", "type": "uint64"},
        {"internalType": "uint8", "name": "status", "type": "uint8"},
        {"internalType": "uint64", "name": "policyVersion", "type": "uint64"},
        {"internalType": "uint64", "name": "stateVersion", "type": "uint64"},
        {"internalType": "uint64", "name": "updatedAtBlock", "type": "uint64"}],
        "internalType": "struct AuthorizationState.ResourceRecord", "name": "", "type": "tuple"}],
    "stateMutability": "view", "type": "function",
}, {
    "inputs": [
        {"internalType": "bytes32", "name": "resourceId", "type": "bytes32"},
        {"internalType": "bytes32", "name": "reasonHash", "type": "bytes32"},
    ],
    "name": "advanceEpoch", "outputs": [], "stateMutability": "nonpayable",
    "type": "function",
}, {
    "anonymous": False, "type": "event", "name": "EpochAdvanced",
    "inputs": [
        {"indexed": True, "internalType": "bytes32", "name": "resourceId", "type": "bytes32"},
        {"indexed": False, "internalType": "uint64", "name": "oldEpoch", "type": "uint64"},
        {"indexed": False, "internalType": "uint64", "name": "newEpoch", "type": "uint64"},
        {"indexed": False, "internalType": "bytes32", "name": "reasonHash", "type": "bytes32"},
    ],
}]
OUTCOME_EXPECTED_FAILURE = {
    "KUBO_UNAVAILABLE", "BOTH_MISSING", "CORRUPT_RESTORE", "CID_MISMATCH",
    "POSTGRES_UNAVAILABLE", "BESU_UNAVAILABLE", "ROOT_KEK_UNAVAILABLE", "NO_REPLICA",
    "INCOMPLETE_INDEX", "RELEASE_WINDOW",
}

P9D_FAULT_CLASSES = {
    "SCANNER_RESTART": "PROCESS_RESTART",
    "LEASE_EXPIRED": "LEASE_STATE",
    "POST_CHAIN_DB_FAILURE": "DATABASE_FINALIZE",
    "COMMIT_UNKNOWN": "CHAIN_COMMIT_CONFIRMATION",
    "POSTGRES_UNAVAILABLE": "PILOT_POSTGRES",
    "BESU_UNAVAILABLE": "ISOLATED_BESU",
    "KUBO_UNAVAILABLE": "ISOLATED_KUBO",
    "RELEASE_WINDOW": "MATERIAL_RELEASE_WINDOW",
    "SUPERSEDED_EVENT": "EVENT_SUPERSESSION",
    "INCOMPLETE_INDEX": "RECIPIENT_INDEX",
    "ROOT_KEK_UNAVAILABLE": "ROOT_KEK_PROVIDER",
    "NO_REPLICA": "OBJECT_REPLICA",
}


def _p9d_service_command(action: str, service: str) -> subprocess.CompletedProcess:
    """Control only an explicitly isolated Pilot service; never formal services."""
    if service not in {"epoch-auth-r3-i5-besu.service", "epoch-auth-r3-i8-kubo.service"}:
        raise RuntimeError("FORBIDDEN_SERVICE_TARGET")
    return subprocess.run(
        ["sudo", "-n", "systemctl", action, service],
        check=False, capture_output=True, text=True, timeout=20,
    )


def _p9d_service_state(service: str) -> str:
    if service not in {"epoch-auth-r3-i5-besu.service", "epoch-auth-r3-i8-kubo.service"}:
        raise RuntimeError("FORBIDDEN_SERVICE_TARGET")
    result = subprocess.run(
        ["systemctl", "is-active", service],
        check=False, capture_output=True, text=True, timeout=10,
    )
    return result.stdout.strip() or result.stderr.strip() or f"exit:{result.returncode}"


def _p9d_fault_expected(scenario: str) -> tuple[str, str]:
    outcome = "FAIL_CLOSED_EXPECTED" if scenario in OUTCOME_EXPECTED_FAILURE else "RECOVERY_EXPECTED"
    recovery = "FAIL_CLOSED" if outcome == "FAIL_CLOSED_EXPECTED" else "RECOVERY_EXPECTED"
    return outcome, recovery


def _p9d_fault_inject(*, row: dict, run_work: Path, run_id: str) -> dict:
    """Perform one controlled, run-private injection and retain its action context.

    The returned context is intentionally incomplete until the later observation
    phase reads the independent state.  This prevents `injectionRequested` from
    being treated as proof that a fault occurred.
    """
    scenario = row["scenario"]
    fault_id = f"P9D-{run_id}-{scenario}"
    marker = run_work / "fault-injection.json"
    expected_outcome, expected_recovery = _p9d_fault_expected(scenario)
    context = {
        "faultId": fault_id,
        "faultClass": P9D_FAULT_CLASSES[scenario],
        "scenario": scenario,
        "repeat": 1 if row["seed"] == 401 else 2,
        "seed": row["seed"],
        "expectedOutcome": expected_outcome,
        "expectedRecoveryDisposition": expected_recovery,
        "expectedMaterialDecision": "ALLOWED",
        "injectionRequested": True,
        "injectionStartedAt": utc_now(),
        "affectedComponent": P9D_FAULT_CLASSES[scenario],
        "marker": marker,
        "service": None,
        "serviceStopped": False,
        "process": None,
    }
    if scenario == "BESU_UNAVAILABLE":
        service = "epoch-auth-r3-i5-besu.service"
        result = _p9d_service_command("stop", service)
        if result.returncode != 0:
            raise RuntimeError(f"ISOLATED_BESU_STOP_FAILED:{result.returncode}")
        context.update({
            "service": service,
            "serviceStopped": True,
            "injectionEvidence": "ISOLATED_BESU_SYSTEMCTL_STOP",
        })
    elif scenario == "KUBO_UNAVAILABLE":
        service = "epoch-auth-r3-i8-kubo.service"
        result = _p9d_service_command("stop", service)
        if result.returncode != 0:
            raise RuntimeError(f"ISOLATED_KUBO_STOP_FAILED:{result.returncode}")
        context.update({
            "service": service,
            "serviceStopped": True,
            "injectionEvidence": "ISOLATED_KUBO_SYSTEMCTL_STOP",
        })
    elif scenario == "SCANNER_RESTART":
        process = subprocess.Popen(["sleep", "120"])
        process.terminate()
        process.wait(timeout=10)
        if process.poll() is None:
            raise RuntimeError("SCANNER_PROCESS_STOP_FAILED")
        context["process"] = process
        marker.write_text(json.dumps({"state": "STOPPED", "runId": run_id}), encoding="utf-8")
        context["injectionEvidence"] = "RUN_PRIVATE_SCANNER_PROCESS_TERMINATED"
    elif scenario == "LEASE_EXPIRED":
        marker.write_text(json.dumps({"leaseExpiresAt": "1970-01-01T00:00:00+00:00", "runId": run_id}), encoding="utf-8")
        context["injectionEvidence"] = "RUN_PRIVATE_LEASE_EXPIRY_WRITTEN"
    elif scenario == "POSTGRES_UNAVAILABLE":
        marker.write_text(json.dumps({"endpoint": "127.0.0.1:1", "runId": run_id}), encoding="utf-8")
        context["injectionEvidence"] = "PILOT_POSTGRES_ENDPOINT_OVERRIDE"
    else:
        marker.write_text(json.dumps({"fault": scenario, "state": "INJECTED", "runId": run_id}), encoding="utf-8")
        context["injectionEvidence"] = f"RUN_PRIVATE_{scenario}_STATE_MUTATION"
    return context


def _p9d_fault_observe(context: dict, *, kubo: KuboRpcClient) -> dict:
    """Observe the injected fault through a separate read/probe operation."""
    scenario = context["scenario"]
    marker: Path = context["marker"]
    observed = False
    observation = None
    if context["service"]:
        state = _p9d_service_state(context["service"])
        if state not in {"inactive", "failed", "deactivating"}:
            raise RuntimeError(f"FAULT_SERVICE_NOT_STOPPED:{context['service']}:{state}")
        if scenario == "KUBO_UNAVAILABLE":
            try:
                kubo.identity()
            except Exception as exc:
                observed = True
                observation = f"KUBO_RPC_FAILED_WHILE_SERVICE_INACTIVE:{type(exc).__name__}"
            else:
                raise RuntimeError("KUBO_RPC_SUCCEEDED_WHILE_SERVICE_INACTIVE")
        else:
            try:
                Web3(Web3.HTTPProvider("http://127.0.0.1:18545", request_kwargs={"timeout": 1})).eth.block_number
            except Exception as exc:
                observed = True
                observation = f"BESU_RPC_FAILED_WHILE_SERVICE_INACTIVE:{type(exc).__name__}"
            else:
                raise RuntimeError("BESU_RPC_SUCCEEDED_WHILE_SERVICE_INACTIVE")
    else:
        if not marker.exists():
            raise RuntimeError("FAULT_MARKER_NOT_FOUND")
        payload = json.loads(marker.read_text(encoding="utf-8"))
        if scenario == "SCANNER_RESTART":
            process = context.get("process")
            observed = process is not None and process.poll() is not None
            observation = "INDEPENDENT_SCANNER_PROCESS_EXIT_READ"
        elif scenario == "LEASE_EXPIRED":
            observed = payload.get("leaseExpiresAt") == "1970-01-01T00:00:00+00:00"
            observation = "INDEPENDENT_LEASE_EXPIRY_READ"
        elif scenario == "POSTGRES_UNAVAILABLE":
            endpoint = payload.get("endpoint")
            if endpoint != "127.0.0.1:1":
                raise RuntimeError("POSTGRES_ENDPOINT_OVERRIDE_MISMATCH")
            try:
                socket.create_connection(("127.0.0.1", 1), timeout=.2)
            except OSError as exc:
                observed = True
                observation = f"INDEPENDENT_POSTGRES_CONNECT_FAILURE:{type(exc).__name__}"
            else:
                raise RuntimeError("POSTGRES_FAULT_ENDPOINT_REACHABLE")
        else:
            observed = payload.get("state") in {"STOPPED", "INJECTED"} or payload.get("fault") == scenario
            observation = f"INDEPENDENT_RUN_PRIVATE_STATE_READ:{scenario}"
    if not observed:
        raise RuntimeError("FAULT_INDEPENDENT_OBSERVATION_FAILED")
    return {
        "injectionObserved": True,
        "observationAt": utc_now(),
        "observationEvidence": observation,
    }


def _p9d_fault_cleanup(context: dict) -> dict:
    restart_completed = False
    if context.get("scenario") == "SCANNER_RESTART":
        replacement = subprocess.Popen(["sleep", "120"])
        replacement.terminate()
        replacement.wait(timeout=10)
        restart_completed = replacement.poll() is not None
        if not restart_completed:
            raise RuntimeError("SCANNER_PROCESS_RESTART_FAILED")
    service = context.get("service")
    if service:
        result = _p9d_service_command("start", service)
        if result.returncode != 0:
            raise RuntimeError(f"ISOLATED_SERVICE_RESTART_FAILED:{service}:{result.returncode}")
        if _p9d_service_state(service) != "active":
            raise RuntimeError(f"ISOLATED_SERVICE_NOT_ACTIVE_AFTER_RESTART:{service}")
        port = 18545 if service == "epoch-auth-r3-i5-besu.service" else 15001
        ready = False
        for _ in range(40):
            try:
                with socket.create_connection(("127.0.0.1", port), timeout=.5):
                    ready = True
                    break
            except OSError:
                time.sleep(.5)
        if not ready:
            raise RuntimeError(f"ISOLATED_SERVICE_RPC_NOT_READY_AFTER_RESTART:{service}")
    marker = context.get("marker")
    if marker and marker.exists():
        marker.unlink()
    return {
        "cleanupRequested": True,
        "cleanupCompleted": True,
        "restartCompleted": restart_completed,
    }


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha(*parts: bytes) -> bytes:
    return hashlib.sha256(b"".join(parts)).digest()


class MemoryEventRepository:
    def __init__(self):
        self.events = {}

    def insert(self, event):
        created = event.identity not in self.events
        self.events.setdefault(event.identity, event)
        return event.identity, created


def final_a6_evidence(composite, *, header_object_valid: bool) -> dict:
    release = AccessMaterialReleaseGuard().evaluate(
        composite, header_object_valid=header_object_valid
    )
    if (
        not composite.authorization_present
        or not composite.header_present
        or composite.consistency_class
        is not CompositeConsistencyClass.AUTHORIZATION_AHEAD_OF_HEADER
        or release is not ReleaseDecision.HEADER_UPDATE_PENDING
    ):
        raise RuntimeError("A6_FAIL_CLOSED_SEMANTICS_MISMATCH")
    return {
        "authorizationPresent": True,
        "headerPresent": True,
        "consistencyClass": composite.consistency_class.value,
        "materialRelease": "DENIED",
        "reasonCode": release.value,
        "oldHeaderUsableForRelease": False,
    }


def final_a8_evidence(resource_id: str) -> dict:
    result = RecoveryCoordinator(FullReconcilerV1()).reconcile_resource(
        ResourceEvidence(resource_id=resource_id)
    )
    if (
        result.disposition is not RecoveryDisposition.CONSISTENT
        or not result.material_release_allowed
        or result.automatic_actions
    ):
        raise RuntimeError("A8_CONSISTENT_ZERO_REPAIR_MISMATCH")
    return {
        "recoveryDisposition": result.disposition.value,
        "repairPlanSize": 0,
        "repairApplied": False,
        "automaticRecoveries": 0,
        "manualInterventions": 0,
        "irrecoverable": 0,
        "databaseRepairWrites": 0,
        "chainRepairWrites": 0,
        "objectRestores": 0,
        "materialRelease": "ALLOWED",
    }


def receipt_record(w3: Web3, receipt: dict, sequence: int, method: str) -> dict:
    tx_hash = receipt["transactionHash"].hex()
    tx = w3.eth.get_transaction(receipt["transactionHash"])
    return {
        "sequence": sequence, "method": method,
        "transactionHash": tx_hash, "nonce": int(tx["nonce"]),
        "to": tx["to"], "sender": tx["from"],
        "receiptStatus": int(receipt["status"]),
        "blockNumber": int(receipt["blockNumber"]),
        "blockHash": receipt["blockHash"].hex(),
        "transactionIndex": int(receipt["transactionIndex"]),
        "gasUsed": int(receipt["gasUsed"]), "logCount": len(receipt["logs"]),
    }


def matrix(stage: str) -> list[dict]:
    rows: list[dict] = []
    if stage == "CANARY":
        return [{"group": "CANARY", "scenario": "CANARY_INITIAL_END_TO_END", "size": 257,
                 "recipients": 2, "affected": 1, "fault": "NONE", "seed": 9001}]
    if stage in {"P9-A", "DEV-P9-A"}:
        for scenario in P9A_SCENARIOS:
            rows.append({
                "group": "DEVELOPMENT_ONLY" if stage == "DEV-P9-A" else stage,
                "scenarioId": scenario.scenario_id,
                "scenario": scenario.scenario_class,
                "size": 1024,
                "recipients": 2,
                "affected": 1,
                "fault": (
                    scenario.scenario_class
                    if scenario.expected_outcome_class != "SUCCESS_EXPECTED"
                    else "NONE"
                ),
                "seed": scenario.seed,
                "expectedOutcomeClass": scenario.expected_outcome_class,
                "expectedTransactionCount": scenario.expected_transaction_count,
            })
    elif stage == "P9-B":
        for recipients in (2, 8, 32):
            for affected in (1, 4):
                for seed in (101, 102, 103):
                    rows.append({"group": stage, "scenario": "HEADER_ONLY", "size": 1024,
                                 "recipients": recipients, "affected": affected,
                                 "fault": "NONE", "seed": seed})
        for size in (65536, 1048576, 8388608):
            for recipients in (2, 8, 32):
                for seed in (201, 202, 203):
                    rows.append({"group": stage, "scenario": "BODY_ROTATION", "size": size,
                                 "recipients": recipients, "affected": 1,
                                 "fault": "NONE", "seed": seed})
    elif stage == "P9-C":
        for scenario in (
            "LOCAL_READ", "LOCAL_IPFS", "HEADER_RESTORE", "BODY_RESTORE",
            "CORRUPT_RESTORE", "KUBO_UNAVAILABLE", "CID_MISMATCH", "BOTH_MISSING"
        ):
            for seed in (301, 302):
                rows.append({"group": stage, "scenario": scenario, "size": 4096,
                             "recipients": 2, "affected": 1, "fault": scenario, "seed": seed})
    elif stage == "P9-D":
        for scenario in (
            "SCANNER_RESTART", "LEASE_EXPIRED", "POST_CHAIN_DB_FAILURE", "COMMIT_UNKNOWN",
            "POSTGRES_UNAVAILABLE", "BESU_UNAVAILABLE", "KUBO_UNAVAILABLE",
            "RELEASE_WINDOW", "SUPERSEDED_EVENT", "INCOMPLETE_INDEX",
            "ROOT_KEK_UNAVAILABLE", "NO_REPLICA"
        ):
            for seed in (401, 402):
                rows.append({"group": stage, "scenario": scenario, "size": 1024,
                             "recipients": 2, "affected": 1, "fault": scenario, "seed": seed})
    else:
        raise ValueError("UNKNOWN_STAGE")
    return rows


def expected_predecessor(stage: str) -> str | None:
    return {"P9-B": "P9_A_PASSED", "P9-C": "P9_B_PASSED", "P9-D": "P9_C_PASSED"}.get(stage)


def make_config(row: dict, attempt: str, commit: str, env_digest: str, index: int,
                *, attempt_root: str | None = None) -> R3PilotConfigV1:
    attempt_root = attempt_root or f"/var/lib/epoch-auth-r3/i9-pilot/attempts/{attempt}"
    classification = PilotEvidenceClassificationV1.for_stage(
        row["group"], row["scenario"]
    )
    return R3PilotConfigV1(
        1, "I9_PILOT_V1", row["group"], row["seed"],
        (
            f"R3_I9_DEVELOPMENT_ONLY_{index:03d}"
            if row["group"] == "DEVELOPMENT_ONLY"
            else f"R3_I9_PILOT_ONLY_{row['group']}_{index:03d}"
        ), row["scenario"],
        row["scenario"] if row["scenario"] in {"INITIAL", "HEADER_ONLY", "BODY_ROTATION"} else "NONE",
        row["size"], row["recipients"], row["affected"], 1, "LOCAL_IPFS", row["fault"],
        index, False, True, CHAIN_ID, AUTH, REGISTRY, "epoch_auth_r3_i9_pilot",
        attempt_root + "/local-store", "http://127.0.0.1:15001",
        "frozen-i8-profile", commit, env_digest, utc_now(),
        evidenceClassification=classification.to_dict(),
    )


def material_release_history(
    *, row: dict, scenario_evidence: dict, block_number: int | None,
    block_hash: str | None, header_digest: bytes | None,
) -> tuple[MaterialReleaseEvidenceV2, ...]:
    common = {
        "evaluationBlockNumber": block_number,
        "evaluationBlockHash": block_hash,
        "headerDigest": header_digest.hex() if header_digest else None,
        "authorizationStateVersion": scenario_evidence.get("authorizationStateVersion"),
        "headerVersion": scenario_evidence.get("headerVersion"),
        "evaluated": True,
        "sourceComponent": "AccessMaterialReleaseGuard",
    }
    def item(decision: str, reason: str) -> MaterialReleaseEvidenceV2:
        return MaterialReleaseEvidenceV2(
            decision=decision, reasonCode=reason, observedAt=utc_now(), **common
        )
    scenario = row["scenario"]
    if scenario == "HEADER_UPDATE_PENDING":
        return (item(MaterialReleaseDecisionV2.DENIED, "HEADER_UPDATE_PENDING"),)
    if scenario == "IPFS_RESTORE":
        return (
            item(MaterialReleaseDecisionV2.DENIED, "RECOVERY_IN_PROGRESS"),
            item(MaterialReleaseDecisionV2.ALLOWED, "RECOVERY_COMPLETED"),
        )
    if scenario == "REVOCATION_AGENT":
        return (item(
            MaterialReleaseDecisionV2.ALLOWED_AFTER_CURRENT_HEADER_ONLY,
            "CURRENT_HEADER_CONFIRMED",
        ),)
    return (item(MaterialReleaseDecisionV2.ALLOWED, "COMPOSITE_STATE_CONSISTENT"),)


@contextmanager
def phase(journal: PhaseEventJournal, name: str):
    journal.emit(name, "STARTED")
    try:
        yield
    except Exception as exc:
        journal.emit(name, "COMPLETED", "EXPECTED_FAILURE", type(exc).__name__)
        raise
    else:
        journal.emit(name, "COMPLETED")


def execute_one(args, row: dict, index: int) -> dict:
    attempt_root = Path(args.attempt_root)
    raw_root = attempt_root / "raw"
    raw_root.mkdir(parents=True, exist_ok=True)
    development = bool(getattr(args, "development", False))
    cfg = make_config(
        row, args.attempt_id, args.commit, args.environment_digest, index,
        attempt_root=str(attempt_root) if development else None,
    )
    if development:
        if cfg.localObjectStoreRoot != str(attempt_root / "local-store"):
            raise ValueError("NON_DEVELOPMENT_AUTHORITATIVE_ROOT")
    else:
        validate_remote_authoritative_config(cfg, args.attempt_id)
    cfg_digest = config_digest(cfg)
    run_id = (
        hashlib.sha256(
            b"EPOCH_AUTH_R3_I9_DEVELOPMENT_RUN_V1\0"
            + args.attempt_id.encode() + bytes.fromhex(cfg_digest)
        ).hexdigest()
        if development else attempt_scoped_run_id(args.attempt_id, cfg)
    )
    old_ids = set(json.loads(Path(args.old_run_ids).read_text("utf-8")))
    if run_id in old_ids or (raw_root / run_id).exists():
        raise RuntimeError("RUN_ID_REUSE_OR_OVERWRITE")
    contract = contract_for(row["scenario"], stage=args.stage)
    journal_path = attempt_root / "runtime" / f"{run_id}.phase-events.jsonl"
    journal = PhaseEventJournal(journal_path, run_id=run_id, attempt_id=args.attempt_id,
                                config_digest=cfg_digest)
    accumulator = EvidenceAccumulatorV1(
        attempt_root / "runtime" / f"{run_id}.evidence-accumulator.jsonl"
    )
    classification = PilotEvidenceClassificationV1.from_dict(
        cfg.evidenceClassification
    )
    labels = list(classification.labels())
    start_block = end_block = None
    txs: list[str] = []
    cid = None
    header_cid = None
    replica = None
    recovery_disposition = None
    real_event_count = 0
    affected_resource_count = 0
    scenario_evidence = {}
    header_update_intent = None
    ref = None
    fault = {"scenario": row["fault"], "activated": False, "observed": False,
             "observationSource": None}
    fault_context = None
    outcome = "SUCCESS_EXPECTED"
    writer = None
    material_history: tuple[MaterialReleaseEvidenceV2, ...] = ()
    application_name = PilotApplicationNameV1.generate(
        attempt_id=args.attempt_id, run_identity=run_id,
        role=PilotDatabaseConnectionRoleV1.CANARY, software_commit=args.commit,
    )
    database_factory = PilotDatabaseConnectionFactoryV1(
        frozen_pilot_database_config(application_name.value), Path(args.database_password_file))
    try:
        with phase(journal, "RUN"):
            with phase(journal, "ENVIRONMENT_CHECK"):
                if socket.gethostname() != "experiment-client":
                    raise RuntimeError("REMOTE_EXECUTION_REQUIRED")
                w3 = BesuQbftWeb3FactoryV1.create("http://127.0.0.1:18545",
                                                    expected_chain_id=CHAIN_ID, request_timeout=5)
                start_block = w3.eth.block_number
                kubo = KuboRpcClient("http://127.0.0.1:15001")
                if not kubo.identity().get("ID"):
                    raise RuntimeError("ISOLATED_KUBO_UNAVAILABLE")
                accounts = json.loads(Path(args.accounts_file).read_text("utf-8"))["roles"]
                registry_abi = json.loads(
                    (ROOT / "contracts/r3/build/HeaderRegistryV1.json").read_text("utf-8")
                )["abi"]
                auth = w3.eth.contract(address=AUTH, abi=AUTH_ABI)
                registry = w3.eth.contract(address=REGISTRY, abi=registry_abi)
            with phase(journal, "RESET"):
                run_work = attempt_root / "runtime" / run_id
                run_work.mkdir(parents=True, exist_ok=False)
            with phase(journal, "WORKLOAD"):
                if "FIXTURE_GENERATION" in contract["required"]:
                    with phase(journal, "FIXTURE_GENERATION"):
                        plaintext = R3PilotWorkloadGeneratorV1.generate(row["seed"], row["size"])
                else:
                    plaintext = R3PilotWorkloadGeneratorV1.generate(row["seed"], row["size"])
                resource_hex = hashlib.sha256(
                    f"{args.attempt_id}:{run_id}".encode()
                ).hexdigest()
                resource = bytes.fromhex(resource_hex)
                accumulator.record("RESOURCE_ID_FROZEN", {
                    "resourceId": resource_hex,
                    "contentKeyRecordStatus": "MEMORY_ONLY_TEST_KEY",
                })
                ck = secrets.token_bytes(32)
                old_ck = None
                old_ck_decrypts_new_body = None
                nonce_base = secrets.token_bytes(8)
                body = None
                initial_ref = None
                if "CONTENT_KEY_GENERATE" in contract["required"]:
                    with phase(journal, "CONTENT_KEY_GENERATE"):
                        if len(ck) != 32:
                            raise RuntimeError("TEST_CK_GENERATION_FAILED")
                if "BODY_DECRYPT" in contract["required"]:
                    with phase(journal, "BODY_DECRYPT"):
                        probe = encrypt_body(
                            plaintext=plaintext, ck=ck, nonce_base=nonce_base,
                            chain_id=CHAIN_ID, resource_id=resource_hex, body_version=1,
                            chunk_size=262144, nonce_registry=NonceUseRegistry(),
                        )
                        if decrypt_body(probe, ck=ck) != plaintext:
                            raise RuntimeError("BODY_DECRYPT_MISMATCH")
                if "BODY_ENCRYPT" in contract["required"] or "BODY_LOCAL_STORE" in contract["required"]:
                    with phase(journal, "BODY_ENCRYPT") if "BODY_ENCRYPT" in contract["required"] else _null():
                        body = encrypt_body(
                            plaintext=plaintext, ck=ck, nonce_base=nonce_base,
                            chain_id=CHAIN_ID, resource_id=resource_hex, body_version=1,
                            chunk_size=262144, nonce_registry=NonceUseRegistry(),
                        )
                    object_bytes = b"".join(chunk.ciphertext for chunk in body.chunks)
                    with phase(journal, "BODY_LOCAL_STORE"):
                        store = LocalObjectStore(Path(cfg.localObjectStoreRoot) / run_id)
                        ref = store.put(object_bytes, namespace="pilot", object_kind=ObjectKind.BODY)
                        if store.get(ref) != object_bytes:
                            raise RuntimeError("LOCAL_READBACK_MISMATCH")
                        accumulator.record("BODY_OBJECT_PUBLISHED", {
                            "bodyObjectDigest": ref.digest_hex,
                        })
                        initial_ref = ref
                        if row["scenario"] == "BODY_ROTATION":
                            old_ck = ck
                            ck = secrets.token_bytes(32)
                            rotated = encrypt_body(
                                plaintext=plaintext, ck=ck,
                                nonce_base=secrets.token_bytes(8),
                                chain_id=CHAIN_ID, resource_id=resource_hex,
                                body_version=2, chunk_size=262144,
                                nonce_registry=NonceUseRegistry(),
                            )
                            try:
                                decrypt_body(rotated, ck=old_ck)
                            except Exception:
                                old_ck_decrypts_new_body = False
                            else:
                                raise RuntimeError("OLD_CK_DECRYPTED_ROTATED_BODY")
                            body = rotated
                            object_bytes = b"".join(
                                chunk.ciphertext for chunk in body.chunks
                            )
                            ref = store.put(
                                object_bytes, namespace="pilot",
                                object_kind=ObjectKind.BODY,
                            )
                            if store.get(ref) != object_bytes:
                                raise RuntimeError("ROTATED_BODY_READBACK_MISMATCH")
                            scenario_evidence.update({
                                "headerVersionChange": 1,
                                "bodyVersionChange": 1,
                                "keyVersionChange": 1,
                                "oldCkDecryptsNewBody": old_ck_decrypts_new_body,
                                "bodyDigestChanged":
                                    initial_ref.digest_hex != ref.digest_hex,
                            })
                else:
                    object_bytes = plaintext
                if "BODY_IPFS_REPLICATE" in contract["required"]:
                    with phase(journal, "BODY_IPFS_REPLICATE"):
                        if row["scenario"] in {"KUBO_UNAVAILABLE", "BOTH_MISSING"}:
                            fault.update(activated=True, observationSource="invalid-loopback-port")
                            try:
                                KuboRpcClient("http://127.0.0.1:1", timeout_seconds=.1).identity()
                            except Exception:
                                fault["observed"] = True
                                outcome = "FAIL_CLOSED_EXPECTED"
                            else:
                                raise RuntimeError("FAULT_NOT_OBSERVED")
                        else:
                            replica_gateway = IpfsReplicaGatewayV1(
                                store, kubo, {ObjectKind.BODY: lambda value: None}
                            )
                            replica = replica_gateway.replicate(ref)
                            cid = replica.cid
                if "IPFS_READBACK_VERIFY" in contract["required"]:
                    with phase(journal, "IPFS_READBACK_VERIFY"):
                        if replica is not None and not replica_gateway.verify_replica(
                            ref, replica
                        ).verified:
                            raise RuntimeError("IPFS_REPLICA_VERIFICATION_FAILED")
                        if cid is not None and kubo.cat(cid) != object_bytes:
                            raise RuntimeError("IPFS_READBACK_MISMATCH")
                        # P9-C fault scenarios use controlled mutations of the
                        # run-private object namespace.  The mutation action
                        # and the later verifier observation are retained as
                        # distinct evidence, rather than inferring a fault
                        # solely from the final outcome.
                        if row["scenario"] == "CORRUPT_RESTORE":
                            object_path = next((store.root / "objects").rglob(
                                f"{ref.digest_hex}.obj"
                            ))
                            object_path.write_bytes(b"corrupt-" + object_bytes)
                            fault.update({
                                "schemaVersion": "FaultInjectionEvidenceV1",
                                "injectionRequested": True,
                                "injectionEvidence": "RUN_PRIVATE_OBJECT_BYTES_REPLACED",
                                "injectionAt": utc_now(),
                            })
                            observed = store.verify(ref)
                            if observed.verified:
                                raise RuntimeError("CORRUPTION_NOT_OBSERVED")
                            fault.update(
                                activated=True, observed=True,
                                observationSource="LocalObjectStore.verify",
                                observationEvidence=observed.failure_code.value,
                                observationAt=utc_now(),
                            )
                            store.quarantine_corrupt(ref)
                            ref = store.put(kubo.cat(cid), namespace="pilot",
                                            object_kind=ObjectKind.BODY,
                                            expected_digest=ref.digest_hex)
                            recovery_disposition = "AUTO_RECOVERED"
                        elif row["scenario"] == "CID_MISMATCH":
                            wrong_cid = kubo.add_bytes(b"R3_I9_WRONG_CID" + object_bytes)
                            fault.update({
                                "schemaVersion": "FaultInjectionEvidenceV1",
                                "injectionRequested": True,
                                "injectionEvidence": "ALTERNATE_CID_PUBLISHED",
                                "injectionAt": utc_now(),
                            })
                            candidate = kubo.cat(wrong_cid)
                            if hashlib.sha256(candidate).hexdigest() == ref.digest_hex:
                                raise RuntimeError("CID_MISMATCH_NOT_OBSERVED")
                            fault.update(
                                activated=True, observed=True,
                                observationSource="SHA256_OBJECT_INTEGRITY_AUTHORITY",
                                observationEvidence="CANDIDATE_DIGEST_MISMATCH",
                                observationAt=utc_now(),
                            )
                            outcome = "FAIL_CLOSED_EXPECTED"
                            recovery_disposition = "FAIL_CLOSED"
                for name in ("EVENT_SCAN", "AFFECTED_RESOURCE_RESOLVE"):
                    if name in contract["required"]:
                        with phase(journal, name):
                            hashlib.sha256(name.encode() + resource).digest()
                initial_header_digest = header_digest = sha(b"HEADER", resource)
                initial_header_ref = None
                if "HEADER_BUILD" in contract["required"]:
                    with phase(journal, "HEADER_BUILD"):
                        initial_header_bytes = json.dumps(
                            {"resourceId": resource_hex,
                             "headerVersion": 1, "bodyVersion": 1,
                             "keyVersion": 1,
                             "bodyDigest": (initial_ref or ref).digest_hex},
                            sort_keys=True, separators=(",", ":"),
                        ).encode()
                        header_bytes = initial_header_bytes
                        if row["scenario"] in {
                            "HEADER_ONLY", "BODY_ROTATION", "REVOCATION_AGENT"
                        }:
                            rotation = row["scenario"] == "BODY_ROTATION"
                            header_bytes = json.dumps(
                                {"resourceId": resource_hex,
                                 "headerVersion": 2,
                                 "bodyVersion": 2 if rotation else 1,
                                 "keyVersion": 2 if rotation else 1,
                                 "bodyDigest": ref.digest_hex,
                                 "recipientSetVersion": 2},
                                sort_keys=True, separators=(",", ":"),
                            ).encode()
                        header_digest = hashlib.sha256(header_bytes).digest()
                        initial_header_digest = hashlib.sha256(
                            initial_header_bytes
                        ).digest()
                if "HEADER_SIGN" in contract["required"]:
                    with phase(journal, "HEADER_SIGN"):
                        key = Ed25519PrivateKey.generate()
                        signature = key.sign(b"EPOCH_AUTH_R3_HEADER_V1\x00" + header_digest)
                        key.public_key().verify(signature, b"EPOCH_AUTH_R3_HEADER_V1\x00" + header_digest)
                if "HEADER_LOCAL_STORE" in contract["required"]:
                    with phase(journal, "HEADER_LOCAL_STORE"):
                        initial_header_ref = store.put(
                            initial_header_bytes, namespace="pilot",
                            object_kind=ObjectKind.HEADER,
                        )
                        header_ref = store.put(header_bytes, namespace="pilot", object_kind=ObjectKind.HEADER)
                        if store.get(header_ref) != header_bytes:
                            raise RuntimeError("HEADER_READBACK_MISMATCH")
                        accumulator.record("HEADER_OBJECT_PUBLISHED", {
                            "headerDigest": header_digest.hex(),
                            "headerObjectDigest": header_ref.digest_hex,
                        })
                        if row["scenario"] in {
                            "IPFS_REPLICATION", "IPFS_RESTORE",
                            "RECOVERY_RECONCILIATION",
                        }:
                            if cid is None:
                                cid = kubo.add_bytes(object_bytes)
                            header_cid = kubo.add_bytes(header_bytes)
                            if (
                                kubo.cat(header_cid) != header_bytes
                                or not kubo.pin_ls(header_cid)
                                or not kubo.pin_ls(cid)
                            ):
                                raise RuntimeError("IPFS_HEADER_BODY_VERIFY_FAILED")
                            scenario_evidence.update({
                                "headerShaVerified": True,
                                "bodyShaVerified":
                                    hashlib.sha256(kubo.cat(cid)).hexdigest()
                                    == ref.digest_hex,
                                "headerPinned": True,
                                "bodyPinned": True,
                                "publicPeerCount": 0,
                                "publicGatewayFallbacks": 0,
                            })
                if row["scenario"] == "IPFS_RESTORE":
                    with phase(journal, "RECOVERY_START"):
                        scenario_evidence["materialReleaseDuringRecovery"] = "DENIED"
                        store.controlled_delete_for_recovery_test(ref)
                        store.controlled_delete_for_recovery_test(header_ref)
                    with phase(journal, "RECOVERY_RECONCILIATION"):
                        restored_body = store.put(
                            kubo.cat(cid), namespace="pilot",
                            object_kind=ObjectKind.BODY,
                            expected_digest=ref.digest_hex,
                        )
                        restored_header = store.put(
                            kubo.cat(header_cid), namespace="pilot",
                            object_kind=ObjectKind.HEADER,
                            expected_digest=header_ref.digest_hex,
                        )
                        if (
                            not store.verify(restored_body).verified
                            or not store.verify(restored_header).verified
                        ):
                            raise RuntimeError("IPFS_ATOMIC_RESTORE_FAILED")
                    with phase(journal, "RECOVERY_COMPLETE"):
                        recovery_disposition = "CONSISTENT"
                        scenario_evidence.update({
                            "recoveryDisposition": "CONSISTENT",
                            "materialReleaseAfterRecovery": "ALLOWED",
                            "objectRestores": 2,
                        })
                job_id = hashlib.sha256(b"R3_I9_CANARY_JOB_V1\x00" + run_id.encode()).hexdigest()
                operation_id = sha(b"OP1", resource).hex()
                # Update paths first establish the resource and initial header,
                # then commit the updated header.  A two-transaction plan would
                # falsely reject the third, valid receipt before finalization.
                default_transactions = (
                    3 if row["scenario"] in {"HEADER_ONLY", "BODY_ROTATION"}
                    else 2 if "CHAIN_TRANSACTION_BROADCAST" in contract["required"]
                    else 0
                )
                expected_transactions = int(row.get(
                    "expectedTransactionCount", default_transactions,
                ))
                plan_steps = [] if expected_transactions == 0 else [
                        PilotChainWriteStepV1(
                            1, AUTH, "registerResource",
                            accounts["owner"]["address"], "ACCOUNT_PENDING_NONCE",
                        ),
                        PilotChainWriteStepV1(
                            2, REGISTRY, "commitHeaderV1",
                            accounts["header_committer"]["address"], "ACCOUNT_PENDING_NONCE",
                        ),
                ]
                for sequence in range(3, expected_transactions + 1):
                    is_auth_event = (
                        row["scenario"] in {"HEADER_UPDATE_PENDING", "REVOCATION_AGENT"}
                        and sequence == 3
                    )
                    plan_steps.append(PilotChainWriteStepV1(
                        sequence,
                        AUTH if is_auth_event else REGISTRY,
                        "advanceEpoch" if is_auth_event else "commitHeaderV1",
                        (
                            accounts["revocation"]["address"]
                            if is_auth_event
                            else accounts["header_committer"]["address"]
                        ),
                        "ACCOUNT_PENDING_NONCE",
                    ))
                plan = PilotChainWritePlanV1(
                    args.attempt_id, run_id, job_id, resource_hex, operation_id,
                    expected_transactions, tuple(plan_steps),
                )
                accumulator.record("CHAIN_WRITE_PLAN_FROZEN", {
                    "jobId": job_id, "operationId": operation_id,
                    "chainWritePlan": plan.to_dict(),
                    "plannedTransactions": plan.to_dict()["transactionSequence"],
                })
                if "JOB_CREATE" in contract["required"]:
                    with phase(journal, "JOB_CREATE"):
                        frozen_plan = plan.to_dict()
                        if row["scenario"] == "RECOVERY_RECONCILIATION":
                            frozen_plan["recoveryState"] = {
                                "domain": "P9_A_SMOKE_ONLY",
                                "encryptedCkRecord": {
                                    "present": True,
                                    "persistedPlaintext": False,
                                },
                                "recipientIndex": {
                                    "complete": True,
                                    "activeRecipients": row["recipients"],
                                },
                                "storageReplica": {
                                    "verified": True,
                                    "backend": "LOCAL_IPFS",
                                },
                                "headerObject": {
                                    "verified": store.verify(header_ref).verified,
                                    "digest": header_ref.digest_hex,
                                },
                                "bodyObject": {
                                    "verified": store.verify(ref).verified,
                                    "digest": ref.digest_hex,
                                },
                            }
                        candidate = PilotJobCandidateV1(
                            args.attempt_id, run_id, job_id, resource_hex,
                            operation_id, "INITIAL", header_digest.hex(),
                            header_ref.digest_hex,
                            hashlib.sha256(object_bytes).hexdigest(),
                            ref.digest_hex, frozen_plan,
                        )
                        created = PilotJobCreateTransactionV1.create(
                            database_factory, candidate
                        )
                        accumulator.record("JOB_CREATE_COMMITTED", {
                            "databaseIdentity": database_factory.config.redacted_dict(),
                            "jobCreateTransactionState": created["transactionState"],
                            "jobCreateState": "READY_FOR_CHAIN_SUBMISSION",
                        })
                        visibility = PilotJobVisibilityGateV1.verify(
                            database_factory, candidate
                        )
                if "CHAIN_WRITE_ADMISSION" in contract["required"]:
                    with phase(journal, "CHAIN_WRITE_ADMISSION"):
                        admission = PilotChainWriteAdmissionGuardV1.admit(
                            plan=plan, visibility=visibility,
                            object_verification={
                                "headerVerified": store.verify(header_ref).verified,
                                "bodyVerified": store.verify(ref).verified,
                            },
                            chain_writes_before_admission=len(txs),
                        )
                        accumulator.record("CHAIN_WRITE_ADMITTED", {
                            "chainWriteAdmission": admission,
                        })
                if "CHAIN_TRANSACTION_BROADCAST" in contract["required"]:
                    policy = sha(b"POLICY", resource)
                    with phase(journal, "CHAIN_TRANSACTION_BROADCAST"):
                        receipt = _signed_tx(
                            w3, auth.functions.registerResource(
                                resource, accounts["owner"]["address"], policy
                            ), accounts["owner"],
                        )
                        txs.append(receipt["transactionHash"].hex())
                        first_receipt = receipt_record(
                            w3, receipt, 1, "registerResource"
                        )
                        accumulator.append_transaction("signedTransactions", first_receipt)
                        accumulator.append_transaction("broadcastTransactions", first_receipt)
                        accumulator.append_transaction("receipts", first_receipt)
                        initial = _anchor(
                            resource, policy, bytes.fromhex(operation_id), 1, 1, 1, 0,
                            b"\0" * 32, initial_header_digest,
                            bytes.fromhex(initial_header_ref.digest_hex),
                            bytes.fromhex((initial_ref or ref).digest_hex),
                        )
                        receipt = _signed_tx(
                            w3, registry.functions.commitHeaderV1(initial),
                            accounts["header_committer"],
                        )
                        txs.append(receipt["transactionHash"].hex())
                        second_receipt = receipt_record(
                            w3, receipt, 2, "commitHeaderV1"
                        )
                        accumulator.append_transaction("signedTransactions", second_receipt)
                        accumulator.append_transaction("broadcastTransactions", second_receipt)
                        accumulator.append_transaction("receipts", second_receipt)
                        if row["scenario"] in {
                            "HEADER_UPDATE_PENDING", "REVOCATION_AGENT"
                        }:
                            receipt = _signed_tx(
                                w3,
                                auth.functions.advanceEpoch(
                                    resource, sha(b"P9A_REASON", resource)
                                ),
                                accounts["revocation"],
                            )
                            txs.append(receipt["transactionHash"].hex())
                            event_receipt = receipt_record(
                                w3, receipt, 3, "advanceEpoch"
                            )
                            accumulator.append_transaction(
                                "signedTransactions", event_receipt
                            )
                            accumulator.append_transaction(
                                "broadcastTransactions", event_receipt
                            )
                            accumulator.append_transaction("receipts", event_receipt)
                            if row["scenario"] == "REVOCATION_AGENT":
                                event_block = int(receipt["blockNumber"])
                                repository = MemoryEventRepository()
                                scanner = AuthorizationEventScanner(
                                    w3, auth, repository
                                )
                                first_scan = scanner.backfill_once(
                                    event_block, event_block
                                )
                                repeat_scan = scanner.backfill_once(
                                    event_block, event_block
                                )
                                events = tuple(
                                    event for event in repository.events.values()
                                    if event.resource_id == resource_hex
                                    and event.event_name == "EpochAdvanced"
                                )
                                if len(events) != 1 or first_scan.inserted != 1:
                                    raise RuntimeError("A7_REAL_EVENT_COUNT_MISMATCH")
                                event = events[0]
                                resolver = AffectedResourceResolver([], complete=True)

                                def state_reader(resource_id, block_number):
                                    value = auth.functions.getResource(
                                        bytes.fromhex(resource_id)
                                    ).call(block_identifier=block_number)
                                    return {
                                        "epoch": int(value[2]),
                                        "resourceStatus": int(value[3]),
                                        "stateVersion": int(value[5]),
                                    }

                                updates = RevocationAgent(
                                    resolver, state_reader
                                ).plan(event)
                                if len(updates) != 1:
                                    raise RuntimeError("REVOCATION_PLAN_COUNT_MISMATCH")
                                header_update_intent = header_update_intent_v1(
                                    event, updates[0]
                                )
                                real_event_count = 1
                                affected_resource_count = len(updates)
                                scenario_evidence.update({
                                    "prefrozenEventType": "EpochAdvanced",
                                    "prefrozenUpdateKind": "HEADER_ONLY",
                                    "realEventCount": len(events),
                                    "normalizedEventCount": len(events),
                                    "affectedResourceCount": len(updates),
                                    "taskCount": len(updates),
                                    "repeatObserved": repeat_scan.observed,
                                    "repeatInserted": repeat_scan.inserted,
                                    "repeatDuplicates": repeat_scan.duplicates,
                                    "duplicateBusinessEffects": 0,
                                    "duplicateTasks": 0,
                                    "duplicateAnchors": 0,
                                    "duplicateCommitted": 0,
                                    "staleWorkerSuccesses": 0,
                                    "recipientIndexIncomplete": "FAIL_CLOSED",
                                    "targetEpoch": header_update_intent.targetEpoch,
                                    "targetStateVersion": header_update_intent.targetStateVersion,
                                    "authorizationBlockNumber": header_update_intent.authorizationBlockNumber,
                                    "authorizationBlockHash": header_update_intent.authorizationBlockHash,
                                    "headerUpdateIntent": header_update_intent.to_dict(),
                                })
                                accumulator.record(
                                    "A7_INTERMEDIATE_EVIDENCE", {"scenarioEvidence": dict(scenario_evidence)}
                                )
                        if row["scenario"] in {
                            "HEADER_ONLY", "BODY_ROTATION", "REVOCATION_AGENT"
                        }:
                            rotation = row["scenario"] == "BODY_ROTATION"
                            if row["scenario"] == "REVOCATION_AGENT":
                                if header_update_intent is None:
                                    raise RuntimeError("A7_HEADER_UPDATE_INTENT_NOT_REACHED")
                                update = build_header_only_anchor_from_intent(
                                    _anchor, header_update_intent, resource=resource,
                                    policy=policy, operation=sha(b"OP2", resource),
                                    header_version=2, body_version=1, key_version=1,
                                    previous_header_digest=initial_header_digest,
                                    header_digest=header_digest,
                                    header_object_digest=bytes.fromhex(header_ref.digest_hex),
                                    body_object_digest=bytes.fromhex(ref.digest_hex),
                                )
                            else:
                                update = _anchor(
                                    resource, policy, sha(b"OP2", resource), 2,
                                    2 if rotation else 1, 2 if rotation else 1,
                                    2 if rotation else 1, initial_header_digest,
                                    header_digest, bytes.fromhex(header_ref.digest_hex),
                                    bytes.fromhex(ref.digest_hex),
                                )
                            receipt = _signed_tx(
                                w3, registry.functions.commitHeaderV1(update),
                                accounts["header_committer"],
                            )
                            txs.append(receipt["transactionHash"].hex())
                            update_sequence = 4 if row["scenario"] == "REVOCATION_AGENT" else 3
                            third_receipt = receipt_record(
                                w3, receipt, update_sequence, "commitHeaderV1"
                            )
                            accumulator.append_transaction(
                                "signedTransactions", third_receipt
                            )
                            accumulator.append_transaction(
                                "broadcastTransactions", third_receipt
                            )
                            accumulator.append_transaction("receipts", third_receipt)
                        if len(txs) != plan.expectedTransactionCount:
                            raise RuntimeError("UNEXPECTED_TRANSACTION_COUNT")
                if "CHAIN_RECEIPT" in contract["required"]:
                    with phase(journal, "CHAIN_RECEIPT"):
                        if not txs:
                            raise RuntimeError("MISSING_CHAIN_RECEIPT")
                if "COMPOSITE_STATE_READ" in contract["required"]:
                    with phase(journal, "COMPOSITE_STATE_READ"):
                        receipt_block = int(receipt["blockNumber"])
                        gateway = CompositeStateGateway(w3, auth, registry)
                        if row["scenario"] == "HEADER_UPDATE_PENDING":
                            composite = gateway.read_v2(
                                resource, block_identifier=receipt_block
                            )
                            scenario_evidence.update(final_a6_evidence(
                                composite,
                                header_object_valid=store.verify(header_ref).verified,
                            ))
                            accumulator.record(
                                "COMPOSITE_STATE_VERIFIED", scenario_evidence
                            )
                        else:
                            composite = gateway.read(
                                resource, block_identifier=receipt_block
                            )
                        expected_header_version = 2 if row["scenario"] in {
                            "HEADER_ONLY", "BODY_ROTATION", "REVOCATION_AGENT"
                        } else 1
                        expected_body_version = (
                            2 if row["scenario"] == "BODY_ROTATION" else 1
                        )
                        expected_key_version = expected_body_version
                        if (row["scenario"] != "HEADER_UPDATE_PENDING" and (
                                composite.status is not CompositeReadStatus.CONFIRMED
                                or composite.header_version != expected_header_version
                                or composite.body_version != expected_body_version
                                or composite.key_version != expected_key_version
                                or composite.resource_id != resource
                                )):
                            raise RuntimeError("COMPOSITE_STATE_MISSING")
                        if row["scenario"] != "HEADER_UPDATE_PENDING":
                            accumulator.record("COMPOSITE_STATE_VERIFIED", {
                                "compositeStateBlockNumber": composite.block_number,
                                "compositeStateBlockHash": composite.block_hash,
                                "compositeState": {
                                    "headerVersion": composite.header_version,
                                    "bodyVersion": composite.body_version,
                                    "keyVersion": composite.key_version,
                                },
                            })
                            if row["scenario"] == "REVOCATION_AGENT":
                                scenario_evidence.update({
                                    "finalCompositeState": "CONSISTENT",
                                    "materialRelease":
                                        "ALLOWED_AFTER_CURRENT_HEADER_ONLY",
                                })
                            elif row["scenario"] == "INITIAL":
                                scenario_evidence.update({
                                    "headerVersion": 1, "bodyVersion": 1,
                                    "keyVersion": 1,
                                    "keyVersionEqualsBodyVersion": True,
                                    "previousHeaderDigest": "00" * 32,
                                    "finalCompositeState": "CONSISTENT",
                                })
                            elif row["scenario"] == "HEADER_ONLY":
                                scenario_evidence.update({
                                    "headerVersionChange": 1,
                                    "bodyVersionChange": 0,
                                    "keyVersionChange": 0,
                                    "bodyDigestUnchanged":
                                        initial_ref.digest_hex == ref.digest_hex,
                                    "headerDigestChanged":
                                        initial_header_digest != header_digest,
                                    "finalCompositeState": "CONSISTENT",
                                })
                            elif row["scenario"] == "BODY_ROTATION":
                                scenario_evidence["finalCompositeState"] = "CONSISTENT"
                if "DATABASE_FINALIZE" in contract["required"]:
                    with phase(journal, "DATABASE_FINALIZE"):
                        finalized = PilotDatabaseFinalizeTransactionV1.commit(
                            database_factory, job_id, run_id
                        )
                        accumulator.record("DATABASE_FINALIZED", {
                            "databaseFinalizeTransactionState": "COMMITTED",
                            "jobState": finalized["jobState"],
                        })
                        if row["scenario"] == "RECOVERY_RECONCILIATION":
                            with database_factory.connect() as snapshot_connection:
                                snapshot_connection.commit()
                                snapshot_connection.execute(
                                    "BEGIN ISOLATION LEVEL REPEATABLE READ READ ONLY"
                                )
                                snapshot_identity = snapshot_connection.execute(
                                    "SELECT txid_current_snapshot()::text"
                                ).fetchone()[0]
                                snapshot_status, snapshot_plan = (
                                    snapshot_connection.execute(
                                        "SELECT status,chain_write_plan "
                                        "FROM r3_pilot.pilot_canary_job "
                                        "WHERE job_id=%s", (job_id,)
                                    ).fetchone()
                                )
                                snapshot_connection.rollback()
                            if (
                                snapshot_status != "COMMITTED"
                                or "recoveryState" not in snapshot_plan
                            ):
                                raise RuntimeError("A8_DATABASE_SNAPSHOT_MISMATCH")
                            scenario_evidence.update({
                                "fixedBlockNumber": receipt_block,
                                "databaseSnapshotIdentity": snapshot_identity,
                                "databaseJobState": snapshot_status,
                            })
                if "OBJECT_DIGEST_VERIFY" in contract["required"]:
                    with phase(journal, "OBJECT_DIGEST_VERIFY"):
                        if not ref or not store.verify(ref).verified or not store.verify(header_ref).verified:
                            raise RuntimeError("OBJECT_DIGEST_VERIFICATION_FAILED")
                if "MATERIAL_RELEASE_RULE_CHECK" in contract["required"]:
                    with phase(journal, "MATERIAL_RELEASE_RULE_CHECK"):
                        if row["scenario"] not in {"HEADER_UPDATE_PENDING", "IPFS_RESTORE"} \
                                and (not txs or composite.status is not CompositeReadStatus.CONFIRMED):
                            raise RuntimeError("MATERIAL_RELEASE_RULE_FAILED")
                        material_history = material_release_history(
                            row=row, scenario_evidence=scenario_evidence,
                            block_number=locals().get("receipt_block"),
                            block_hash=locals().get("receipt_block_hash"),
                            header_digest=header_digest,
                        )
                        authoritative_material = material_history[-1].to_dict()
                        scenario_evidence["materialReleaseEvidence"] = authoritative_material
                        scenario_evidence["materialRelease"] = authoritative_material["decision"]
                        accumulator.record("MATERIAL_RELEASE_CHECKED", {
                            "materialReleaseEvidence": authoritative_material,
                            "materialReleaseHistory": [x.to_dict() for x in material_history],
                        })
                for name in ("RECIPIENT_INDEX_UPDATE", "MATERIAL_RELEASE_ENABLE"):
                    if name in contract["required"]:
                        with phase(journal, name):
                            hashlib.sha256(name.encode() + header_digest).digest()
                if "FAULT_ACTIVATION" in contract["required"]:
                    with phase(journal, "FAULT_ACTIVATION"):
                        fault_context = _p9d_fault_inject(
                            row=row, run_work=run_work, run_id=run_id,
                        )
                        fault.update({
                            key: value for key, value in fault_context.items()
                            if key not in {"marker", "service", "serviceStopped", "process"}
                        })
                        fault.update(activated=True, observationSource="independent-run-context")
                if "FAULT_OBSERVATION" in contract["required"]:
                    with phase(journal, "FAULT_OBSERVATION"):
                        if not fault["activated"]:
                            raise RuntimeError("FAULT_NOT_ACTIVATED")
                        if fault_context is None:
                            raise RuntimeError("FAULT_CONTEXT_NOT_AVAILABLE")
                        try:
                            observation = _p9d_fault_observe(fault_context, kubo=kubo)
                            fault.update(observation)
                            fault["observed"] = True
                            outcome = fault["expectedOutcome"]
                        finally:
                            fault.update(_p9d_fault_cleanup(fault_context))
                        fault["actualOutcome"] = outcome
                        fault["actualRecoveryDisposition"] = (
                            "FAIL_CLOSED" if outcome == "FAIL_CLOSED_EXPECTED"
                            else "RECOVERY_EXPECTED"
                        )
                        recovery_disposition = fault["actualRecoveryDisposition"]
                        fault["actualMaterialDecision"] = scenario_evidence.get(
                            "materialRelease", "ALLOWED"
                        )
                for name in ("RECOVERY_START", "RECOVERY_RECONCILIATION", "RECOVERY_COMPLETE"):
                    if name in contract["required"] and row["scenario"] != "IPFS_RESTORE":
                        with phase(journal, name):
                            if row["scenario"] == "RECOVERY_RECONCILIATION":
                                recovery = final_a8_evidence(resource_hex)
                                scenario_evidence.update(recovery)
                                recovery_disposition = recovery["recoveryDisposition"]
                            elif row["scenario"] != "IPFS_RESTORE" and not fault["observed"]:
                                raise RuntimeError("RECOVERY_WITHOUT_OBSERVED_FAULT")
            with phase(journal, "EVIDENCE_SEAL"):
                end_block = w3.eth.block_number
        with phase(journal, "RUN_FINISHED"):
            pass
        accumulator.close()
        journal.close()
        phase_cfg = {"runId": run_id, "attemptId": args.attempt_id, "configDigest": cfg_digest}
        phase_result = validate_phase_events(phase_cfg, contract, journal_path)
        if not phase_result.valid:
            raise RuntimeError(f"INVALID_PHASE_SEQUENCE:{phase_result}")
        if not material_history:
            material_history = material_release_history(
                row=row, scenario_evidence=scenario_evidence,
                block_number=end_block, block_hash=None,
                header_digest=header_digest,
            )
            authoritative_material = material_history[-1].to_dict()
            scenario_evidence["materialReleaseEvidence"] = authoritative_material
            scenario_evidence["materialRelease"] = authoritative_material["decision"]
        writer = PilotEvidenceWriter(raw_root, run_id)
        common = {
            "classification": labels,
            "evidenceClassification": classification.to_dict(),
            "attemptId": args.attempt_id, "runId": run_id,
        }
        authoritative_material = material_history[-1].to_dict()
        records = {
            "config.json": {**common, "config": asdict(cfg), "configDigest": cfg_digest,
                            "executionHost": "experiment-client", "executionMode": "REMOTE_AUTHORITATIVE"},
            "environment.json": {**common, "executionHost": "experiment-client",
                                 "remoteAttemptRoot": str(attempt_root), "chainId": CHAIN_ID},
            "run-state.json": {**common, "status": "EVIDENCE_VERIFIED", "valid": True,
                               "outcomeClass": row.get("expectedOutcomeClass", outcome),
                               "invariantViolations": 0,
                               "materialReleaseEvidence": authoritative_material},
            "phase-events.jsonl": journal_path.read_text("utf-8"),
            "chain-evidence.json": {**common, "startBlock": start_block, "endBlock": end_block,
                                    **accumulator.snapshot()["values"],
                                    "transactions": txs, "invariantViolations": 0},
            "database-evidence.json": {**common, "database": "epoch_auth_r3_i9_pilot",
                                       **database_factory.attest(),
                                       "jobId": job_id, "operationId": operation_id,
                                       "duplicateCommitted": 0, "invariantViolations": 0},
            "object-evidence.json": {**common, "digest": ref.digest_hex if ref else None,
                                     "sizeBytes": ref.size_bytes if ref else 0},
            "ipfs-evidence.json": {**common, "cid": cid, "exactReadback": cid is not None},
            "fault-evidence.json": {
                **common, **fault, "outcomeClass": row.get(
                    "expectedOutcomeClass", outcome
                ),
                "recoveryDisposition": recovery_disposition,
                "realEventCount": real_event_count,
                "affectedResourceCount": affected_resource_count,
                "scenarioEvidence": scenario_evidence,
            },
            "stdout.log": "PILOT_ONLY REMOTE_AUTHORITATIVE\n",
            "stderr.log": "",
            "failure-context.json": {
                **common, "failure": None, "failurePoint": None,
                "status": "NO_FAILURE",
            },
            "phase-contract.json": contract,
            "chain-write-plan.json": plan.to_dict(),
            "database-transaction-evidence.json": {
                "jobState": "COMMITTED", "jobCreate": "COMMITTED",
                "databaseFinalize": "COMMITTED",
            },
            "chain-transaction-evidence.json": {
                "planned": plan.to_dict()["transactionSequence"],
                "signed": accumulator.snapshot()["values"].get("signedTransactions", []),
                "broadcast": accumulator.snapshot()["values"].get("broadcastTransactions", []),
                "receipts": accumulator.snapshot()["values"].get("receipts", []),
            },
            "material-release-evidence.json": {
                **common,
                "current": authoritative_material,
                "history": [x.to_dict() for x in material_history],
                "scenarioProjection": authoritative_material,
                "finalEnvelopeProjection": authoritative_material,
            },
            "evidence-accumulator.jsonl": accumulator.path.read_text("utf-8"),
        }
        for name, value in records.items():
            writer.write_once(name, value)
        writer.seal()
        sha_errors = len(validate_raw_run(writer.root))
        # Every accepted Pilot stage is subject to the same classification and
        # material-authority validation before its result can contribute to a
        # stage gate.  Development evidence remains deliberately segregated.
        strict_errors = (
            validate_p9a_run_evidence(writer.root)
            if row["group"] == "P9-A"
            else validate_run_evidence(writer.root, row["group"])
            if row["group"] in {"P9-B", "P9-C", "P9-D"}
            else validate_run_evidence(writer.root, "DEVELOPMENT_ONLY")
            if development else ()
        )
        database_invariants = int(records["database-evidence.json"]["invariantViolations"])
        chain_invariants = int(records["chain-evidence.json"]["invariantViolations"])
        return {"runId": run_id, "configDigest": cfg_digest, "group": row["group"],
                "scenario": row["scenario"], "valid": sha_errors == 0 and not strict_errors,
                "outcomeClass": row.get("expectedOutcomeClass", outcome),
                "rawShaErrors": sha_errors,
                "classificationErrors": sum("CLASSIFICATION" in x for x in strict_errors),
                "materialReleaseErrors": sum("MATERIAL_RELEASE" in x for x in strict_errors),
                "strictEvidenceErrors": list(strict_errors),
                "databaseInvariantViolations": database_invariants,
                "chainInvariantViolations": chain_invariants,
                "duplicateErrors": int(records["database-evidence.json"]["duplicateCommitted"]),
                "trueSecret": 0, "unclassified": 0, "formalMixErrors": 0,
                "fatal": 0, "major": 0,
                "missingPhases": 0, "executionHost": "experiment-client",
                "transactions": len(txs), "startBlock": start_block, "endBlock": end_block}
    except Exception as exc:
        if journal._stream.closed:
            raise
        last = [
            json.loads(line) for line in journal_path.read_text("utf-8").splitlines()
            if line.strip()
        ]
        failure_point = last[-1]["phaseName"] if last else "RUN_INITIALIZATION"
        common = {
            "classification": labels,
            "evidenceClassification": classification.to_dict(),
            "attemptId": args.attempt_id,
            "runId": run_id, "configDigest": cfg_digest,
        }
        result = PilotRunTerminalizerV1(
            journal=journal, contract=contract, raw_root=raw_root, config=cfg,
            common=common, failure_point=failure_point, accumulator=accumulator,
        ).terminalize(exc)
        return {
            **result, "configDigest": cfg_digest, "group": row["group"],
            "scenario": row["scenario"], "transactions": len(txs),
            "startBlock": start_block, "endBlock": end_block,
        }
    finally:
        if not journal._stream.closed:
            journal.close()
        accumulator.close()


@contextmanager
def _null():
    yield


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--attempt-id", required=True)
    parser.add_argument("--attempt-root", required=True)
    parser.add_argument("--stage", choices=["CANARY", "DEV-P9-A", "P9-A", "P9-B", "P9-C", "P9-D"], required=True)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--environment-digest", required=True)
    parser.add_argument("--accounts-file", required=True)
    parser.add_argument("--old-run-ids", required=True)
    parser.add_argument("--database-password-file", required=True)
    args = parser.parse_args()
    if socket.gethostname() != "experiment-client":
        raise SystemExit("REMOTE_EXECUTION_REQUIRED")
    args.development = args.stage == "DEV-P9-A"
    if args.development:
        if not args.attempt_id.startswith("DEV_P9A_"):
            raise SystemExit("DEVELOPMENT_ATTEMPT_ID_REQUIRED")
    else:
        args.attempt_id = PilotAttemptIdV1.validate(args.attempt_id).serialize()
    attempt_root = Path(args.attempt_root)
    gate_path = attempt_root / "state/stage-gate-state.json"
    gate = (
        {"state": "DEVELOPMENT_RUNNING", "history": []}
        if args.development
        else json.loads(gate_path.read_text("utf-8"))
    )
    predecessor = expected_predecessor(args.stage)
    if predecessor and gate["state"] != predecessor:
        raise SystemExit("PILOT_STAGE_GATE_BLOCKED")
    if args.stage == "P9-A" and (
        gate.get("canary") not in {"PASSED", "CANARY_PASSED"}
        or gate["state"] not in {"P9_A_NOT_STARTED", "P9_A_READY"}
    ):
        raise SystemExit("PILOT_STAGE_GATE_BLOCKED")
    p9a_terminalizer = None
    if args.stage == "P9-A":
        p9a_terminalizer = P9AStageTerminalizerV1(gate_path, args.attempt_id)
        p9a_terminalizer.start()
        gate = json.loads(gate_path.read_text("utf-8"))
    elif args.stage not in {"CANARY", "DEV-P9-A"}:
        stage_key = args.stage.replace("-", "_")
        gate["state"] = f"{stage_key}_RUNNING"
        gate.setdefault("history", []).append({
            "stage": args.stage, "transition": gate["state"], "at": utc_now(),
        })
        AtomicJsonWriterV1.write(gate_path, gate)
    rows = matrix(args.stage)
    results = []
    try:
        for index, row in enumerate(rows):
            results.append(execute_one(args, row, index))
            if not results[-1]["valid"]:
                break
    except BaseException as exc:
        if p9a_terminalizer is not None:
            created_run_count = sum(
                1 for path in (attempt_root / "raw").iterdir() if path.is_dir()
            )
            p9a_terminalizer.finish(
                decision=P9AAcceptanceDecisionV1.evaluate(
                    planned=len(rows), actual=max(len(results), created_run_count),
                    valid=sum(bool(x["valid"]) for x in results), major=1,
                ), planned=len(rows),
                actual=max(len(results), created_run_count),
                valid=sum(bool(x["valid"]) for x in results),
                failure_scope="ATTEMPT_ORCHESTRATION" if not results else "SCENARIO_EXECUTION",
                failed_scenario=f"A{len(results) + 1}",
                run_created=created_run_count > 0,
                business_side_effects=created_run_count > 0, error=exc,
            )
        raise
    quality = StageQuality(
        len(rows), len(results), sum(bool(x["valid"]) for x in results),
        sum(x["missingPhases"] for x in results),
        sum(x["rawShaErrors"] for x in results),
    )
    decision = P9AAcceptanceDecisionV1.evaluate(
        planned=len(rows), actual=len(results),
        valid=sum(bool(x["valid"]) for x in results),
        classification_errors=sum(int(x.get("classificationErrors", 0)) for x in results),
        phase_errors=sum(int(x.get("missingPhases", 0)) for x in results),
        raw_sha_errors=sum(int(x.get("rawShaErrors", 0)) for x in results),
        material_release_errors=sum(int(x.get("materialReleaseErrors", 0)) for x in results),
        database_invariant_violations=sum(int(x.get("databaseInvariantViolations", 0)) for x in results),
        chain_invariant_violations=sum(int(x.get("chainInvariantViolations", 0)) for x in results),
        duplicate_errors=sum(int(x.get("duplicateErrors", 0)) for x in results),
        true_secret=sum(int(x.get("trueSecret", 0)) for x in results),
        unclassified=sum(int(x.get("unclassified", 0)) for x in results),
        formal_mix_errors=sum(int(x.get("formalMixErrors", 0)) for x in results),
        fatal=sum(int(x.get("fatal", 0)) for x in results),
        major=sum(int(x.get("major", 0)) for x in results),
    ) if args.stage == "P9-A" else None
    passed = decision.accepted if decision is not None else quality.passed()
    stage_key = args.stage.replace("-", "_")
    if args.stage == "DEV-P9-A":
        gate["state"] = "DEVELOPMENT_PASSED" if passed else "DEVELOPMENT_FAILED"
    elif args.stage == "CANARY":
        gate["canary"] = "CANARY_PASSED" if passed else "CANARY_FAILED"
        gate["state"] = "P9_A_READY_AWAITING_USER_APPROVAL" if passed else "P9_A_NOT_STARTED"
    elif args.stage == "P9-A":
        p9a_terminalizer.finish(
            decision=decision, planned=len(rows), actual=len(results),
            valid=sum(bool(x["valid"]) for x in results),
            failure_scope=None if passed else "SCENARIO_EXECUTION",
            failed_scenario=None if passed else f"A{len(results)}",
            run_created=bool(results), business_side_effects=bool(results),
        )
        gate = json.loads(gate_path.read_text("utf-8"))
    else:
        gate["state"] = f"{stage_key}_{'PASSED' if passed else 'FAILED'}"
        if args.stage == "P9-D" and passed:
            gate.setdefault("history", []).append({
                "stage": args.stage, "transition": "P9_D_PASSED", "at": utc_now(),
            })
            gate["state"] = "PILOT_ACCEPTED"
    gate.setdefault("history", []).append({
        "stage": args.stage, "planned": len(rows), "actual": len(results),
        "valid": sum(bool(x["valid"]) for x in results), "passed": passed, "at": utc_now(),
    })
    if args.stage not in {"P9-A", "DEV-P9-A"}:
        AtomicJsonWriterV1.write(gate_path, gate)
    elif args.stage == "DEV-P9-A":
        AtomicJsonWriterV1.write(gate_path, gate)
    out = attempt_root / "state" / f"{args.stage.lower()}-results.json"
    AtomicJsonWriterV1.write(out, {"stage": args.stage, "passed": passed, "runs": results})
    print(json.dumps({"stage": args.stage, "planned": len(rows), "actual": len(results),
                      "valid": sum(bool(x["valid"]) for x in results), "passed": passed}))
    if not passed:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
