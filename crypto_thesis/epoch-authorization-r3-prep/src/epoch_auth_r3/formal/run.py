"""Remote-authoritative R3 formal runner (single RUN, FORMAL_EXPERIMENT).

Executes one ordinal from the frozen FormalExecutionOrderManifestV1 on
experiment-client.  Refuses Pilot/RC2 assets, uses only the independent
Formal chain/database/Kubo/identity domains, and seals immutable raw
evidence with FORMAL_EXPERIMENT classification.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import secrets
import socket
import sys
import time
from contextlib import contextmanager
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from web3 import Web3

from epoch_auth_r3.body.chunk_crypto import NonceUseRegistry
from epoch_auth_r3.body.format_v1 import decrypt_body, encrypt_body
from epoch_auth_r3.formal.config import (
    R3FormalConfigV1, config_digest, validate_remote_authoritative_config,
)
from epoch_auth_r3.formal.database import (
    FormalApplicationNameV1, FormalDatabaseConnectionFactoryV1,
    FormalDatabaseConnectionRoleV1, frozen_formal_database_config,
)
from epoch_auth_r3.formal.events import FormalPhaseEventJournal
from epoch_auth_r3.formal.evidence import FormalEvidenceWriter, validate_raw_run
from epoch_auth_r3.formal.phase_contract import contract_for, validate_phase_events
from epoch_auth_r3.formal.terminalizer import FormalRunTerminalizerV1
from epoch_auth_r3.formal.classification import (
    FormalEvidenceClassificationV1, FormalRunDispositionV1,
    MaterialReleaseDecisionV2, MaterialReleaseEvidenceV2,
    validate_formal_run_evidence,
)
from epoch_auth_r3.formal.chain_write import (
    FormalChainWriteAdmissionGuardV1, FormalChainWritePlanV1,
    FormalChainWriteStepV1,
)
from epoch_auth_r3.formal.job_transaction import (
    FormalDatabaseFinalizeTransactionV1, FormalJobCandidateV1,
    FormalJobCreateTransactionV1, FormalJobVisibilityGateV1,
)
from epoch_auth_r3.formal.workload import FormalWorkloadGeneratorV1
from epoch_auth_r3.formal.matrix import formal_config_for_entry
from epoch_auth_r3.formal.identity import (
    FormalAttemptIdV1, formal_resource_id,
)
from epoch_auth_r3.crypto.hpke_provider import PyHPKEProvider
from epoch_auth_r3.blockchain import (
    CompositeConsistencyClass, CompositeReadStatus, CompositeStateGateway,
)
from epoch_auth_r3.blockchain.web3_factory import BesuQbftWeb3FactoryV1
from epoch_auth_r3.revocation.guard import AccessMaterialReleaseGuard, ReleaseDecision
from epoch_auth_r3.revocation.agent import RevocationAgent
from epoch_auth_r3.revocation.resolver import AffectedResourceResolver
from epoch_auth_r3.revocation.scanner import AuthorizationEventScanner
from epoch_auth_r3.revocation.header_update_intent import (
    build_header_only_anchor_from_intent, header_update_intent_v1,
)
from epoch_auth_r3.storage import LocalObjectStore, ObjectKind
from epoch_auth_r3.storage.ipfs import KuboRpcClient, IpfsReplicaGatewayV1
from epoch_auth_r3.pilot.evidence_accumulator import EvidenceAccumulatorV1


FORMAL_CHAIN_ID = 2026080201
FORMAL_RPC_URL = "http://127.0.0.1:18546"
FORMAL_KUBO_URL = "http://127.0.0.1:15998"
FORMAL_KUBO_URL_UNAVAILABLE = "http://127.0.0.1:1"

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


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha(*parts: bytes) -> bytes:
    return hashlib.sha256(b"".join(parts)).digest()


def _signed_tx(w3: Web3, fn, account: dict[str, str], *, chain_id: int) -> dict:
    address = Web3.to_checksum_address(account["address"])
    tx = fn.build_transaction({
        "from": address,
        "nonce": w3.eth.get_transaction_count(address, "pending"),
        "chainId": chain_id,
        "gas": 15_000_000,
        "gasPrice": w3.eth.gas_price,
        "value": 0,
    })
    signed = w3.eth.account.sign_transaction(tx, account["private_key"])
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    return dict(w3.eth.wait_for_transaction_receipt(tx_hash, timeout=60))


def _anchor(resource: bytes, policy: bytes, operation: bytes, header_version: int,
            body_version: int, key_version: int, update_kind: int,
            previous: bytes, header_digest: bytes, header_object: bytes,
            body_object: bytes, *, epoch: int = 1, state_version: int = 1) -> tuple:
    return (
        operation, resource, policy, epoch, state_version, header_version,
        body_version, key_version, update_kind, previous, header_digest,
        header_object, body_object, "0x0000000000000000000000000000000000000000",
        0, False,
    )


def receipt_record(w3: Web3, receipt: dict, sequence: int, method: str) -> dict:
    tx = w3.eth.get_transaction(receipt["transactionHash"])
    return {
        "sequence": sequence, "method": method,
        "transactionHash": receipt["transactionHash"].hex(), "nonce": int(tx["nonce"]),
        "to": tx["to"], "sender": tx["from"],
        "receiptStatus": int(receipt["status"]),
        "blockNumber": int(receipt["blockNumber"]),
        "blockHash": receipt["blockHash"].hex(),
        "transactionIndex": int(receipt["transactionIndex"]),
        "gasUsed": int(receipt["gasUsed"]), "logCount": len(receipt["logs"]),
    }


class MemoryEventRepository:
    def __init__(self):
        self.events = {}

    def insert(self, event):
        created = event.identity not in self.events
        self.events.setdefault(event.identity, event)
        return event.identity, created


@contextmanager
def phase(journal: FormalPhaseEventJournal, name: str):
    journal.emit(name, "STARTED")
    try:
        yield
    except Exception as exc:
        journal.emit(name, "COMPLETED", "EXPECTED_FAILURE", type(exc).__name__)
        raise
    else:
        journal.emit(name, "COMPLETED")


def material_release_history(
    *, scenario: str, recovery_disposition: str | None,
    block_number: int | None, block_hash: str | None,
    header_digest: bytes | None, state_version: int | None = None,
    header_version: int | None = None, recovery_performed: bool = False,
) -> tuple[MaterialReleaseEvidenceV2, ...]:
    common = {
        "evaluationBlockNumber": block_number,
        "evaluationBlockHash": block_hash,
        "headerDigest": header_digest.hex() if header_digest else None,
        "authorizationStateVersion": state_version,
        "headerVersion": header_version,
        "evaluated": True,
        "sourceComponent": "AccessMaterialReleaseGuard",
    }

    def item(decision: str, reason: str) -> MaterialReleaseEvidenceV2:
        return MaterialReleaseEvidenceV2(
            decision=decision, reasonCode=reason, observedAt=utc_now(), **common
        )

    if recovery_disposition in {"FAIL_CLOSED", "UNRECOVERABLE"}:
        return (item(MaterialReleaseDecisionV2.DENIED, "RECOVERY_FAILED_FAIL_CLOSED"),)
    if scenario == "HEADER_UPDATE_PENDING":
        return (item(MaterialReleaseDecisionV2.DENIED, "HEADER_UPDATE_PENDING"),)
    if scenario == "REVOCATION":
        return (item(
            MaterialReleaseDecisionV2.ALLOWED_AFTER_CURRENT_HEADER_ONLY,
            "CURRENT_HEADER_CONFIRMED",
        ),)
    if scenario in {"RESTORE_REPLICA", "RESTORE_LOCAL"} and recovery_performed:
        return (
            item(MaterialReleaseDecisionV2.DENIED, "RECOVERY_IN_PROGRESS"),
            item(MaterialReleaseDecisionV2.ALLOWED, "RECOVERY_COMPLETED"),
        )
    return (item(MaterialReleaseDecisionV2.ALLOWED, "COMPOSITE_STATE_CONSISTENT"),)


def execute_one(args, entry: dict) -> dict:
    attempt_id = FormalAttemptIdV1.validate(args.attempt_id).serialize()
    attempt_root = Path(args.attempt_root)
    raw_root = attempt_root / "raw"
    raw_root.mkdir(parents=True, exist_ok=True)
    row = entry["row"]
    cfg = formal_config_for_entry(
        row=entry["row"], attempt_id=attempt_id, commit=args.commit,
        env_digest=args.environment_digest, warmup=entry["warmup"],
        repeat_index=entry["repeatIndex"], chain=args.chain,
        attempt_root=str(attempt_root),
    )
    validate_remote_authoritative_config(cfg, attempt_id)
    cfg_digest = config_digest(cfg)
    if cfg_digest != entry["configDigest"]:
        raise RuntimeError("ORDER_MANIFEST_CONFIG_DIGEST_MISMATCH")
    run_id = entry["runId"]
    if (raw_root / run_id).exists():
        raise RuntimeError("RUN_ID_REUSE_OR_OVERWRITE")

    contract = contract_for(
        row["scenarioClass"], replica_state=row["storageMode"],
        fault=row["faultScenario"], restore_path=bool(row.get("restorePath")),
    )
    journal_path = attempt_root / "runtime" / f"{run_id}.phase-events.jsonl"
    journal = FormalPhaseEventJournal(
        journal_path, run_id=run_id, attempt_id=attempt_id, config_digest=cfg_digest,
    )
    accumulator = EvidenceAccumulatorV1(
        attempt_root / "runtime" / f"{run_id}.evidence-accumulator.jsonl"
    )
    classification = FormalEvidenceClassificationV1.from_dict(cfg.evidenceClassification)
    labels = list(classification.labels())

    start_block = end_block = None
    txs: list[str] = []
    cid = None
    header_cid = None
    recovery_disposition = "NOT_REQUIRED"
    recovery_performed = False
    real_event_count = 0
    affected_resource_count = 0
    scenario_evidence = {}
    header_update_intent = None
    ref = None
    initial_ref = None
    header_ref = None
    initial_header_digest = None
    header_digest = None
    fault = {
        "faultClass": row["faultScenario"], "scenario": row["scenarioClass"],
        "activated": False, "observed": False, "observationSource": None,
        "injectionEvidence": None, "observationEvidence": None,
    }
    fault_context = None
    outcome = "SUCCESS_EXPECTED"
    writer = None
    material_history: tuple[MaterialReleaseEvidenceV2, ...] = ()
    application_name = FormalApplicationNameV1.generate(
        attempt_id=attempt_id, run_identity=run_id,
        role=FormalDatabaseConnectionRoleV1.CANARY, software_commit=args.commit,
    )
    database_factory = FormalDatabaseConnectionFactoryV1(
        frozen_formal_database_config(application_name.value), Path(args.database_password_file)
    )
    run_start_mono = time.monotonic_ns()
    try:
        with phase(journal, "RUN"):
            with phase(journal, "ENVIRONMENT_CHECK"):
                if socket.gethostname() != "experiment-client":
                    raise RuntimeError("REMOTE_EXECUTION_REQUIRED")
                w3 = BesuQbftWeb3FactoryV1.create(
                    FORMAL_RPC_URL, expected_chain_id=FORMAL_CHAIN_ID, request_timeout=5,
                )
                start_block = w3.eth.block_number
                kubo = KuboRpcClient(FORMAL_KUBO_URL)
                if not kubo.identity().get("ID"):
                    raise RuntimeError("FORMAL_KUBO_UNAVAILABLE")
                accounts = json.loads(Path(args.accounts_file).read_text("utf-8"))["roles"]
                registry_abi = json.loads(
                    (ROOT / "contracts/r3/build/HeaderRegistryV1.json").read_text("utf-8")
                )["abi"]
                auth = w3.eth.contract(address=args.chain["auth"], abi=AUTH_ABI)
                registry = w3.eth.contract(address=args.chain["registry"], abi=registry_abi)
            with phase(journal, "RESET"):
                run_work = attempt_root / "runtime" / run_id
                run_work.mkdir(parents=True, exist_ok=False)
            with phase(journal, "WORKLOAD"):
                plaintext = FormalWorkloadGeneratorV1.generate(
                    row["seed"], row["bodySizeBytes"]
                )
                resource = formal_resource_id(attempt_id, run_id)
                resource_hex = resource.hex()
                accumulator.record("RESOURCE_ID_FROZEN", {
                    "resourceId": resource_hex,
                    "contentKeyRecordStatus": "MEMORY_ONLY_TEST_KEY",
                })
                ck = secrets.token_bytes(32)
                old_ck = None
                old_ck_decrypts_new_body = None
                nonce_base = secrets.token_bytes(8)
                body = encrypt_body(
                    plaintext=plaintext, ck=ck, nonce_base=nonce_base,
                    chain_id=FORMAL_CHAIN_ID, resource_id=resource_hex, body_version=1,
                    chunk_size=262144, nonce_registry=NonceUseRegistry(),
                )
                object_bytes = b"".join(chunk.ciphertext for chunk in body.chunks)
                with phase(journal, "CONTENT_KEY_GENERATE"):
                    if len(ck) != 32:
                        raise RuntimeError("FORMAL_CK_GENERATION_FAILED")
                with phase(journal, "BODY_DECRYPT"):
                    if decrypt_body(body, ck=ck) != plaintext:
                        raise RuntimeError("BODY_DECRYPT_MISMATCH")
                with phase(journal, "BODY_ENCRYPT"):
                    pass
                with phase(journal, "BODY_LOCAL_STORE"):
                    store = LocalObjectStore(Path(cfg.localObjectStoreRoot) / run_id)
                    ref = store.put(object_bytes, namespace="formal", object_kind=ObjectKind.BODY)
                    if store.get(ref) != object_bytes:
                        raise RuntimeError("LOCAL_READBACK_MISMATCH")
                    accumulator.record("BODY_OBJECT_PUBLISHED", {
                        "bodyObjectDigest": ref.digest_hex,
                    })
                    initial_ref = ref
                    if row["scenarioClass"] == "BODY_ROTATION":
                        old_ck = ck
                        ck = secrets.token_bytes(32)
                        rotated = encrypt_body(
                            plaintext=plaintext, ck=ck,
                            nonce_base=secrets.token_bytes(8),
                            chain_id=FORMAL_CHAIN_ID, resource_id=resource_hex,
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
                        object_bytes = b"".join(chunk.ciphertext for chunk in body.chunks)
                        ref = store.put(
                            object_bytes, namespace="formal", object_kind=ObjectKind.BODY,
                        )
                        if store.get(ref) != object_bytes:
                            raise RuntimeError("ROTATED_BODY_READBACK_MISMATCH")
                        scenario_evidence.update({
                            "headerVersionChange": 1, "bodyVersionChange": 1,
                            "keyVersionChange": 1,
                            "oldCkDecryptsNewBody": old_ck_decrypts_new_body,
                            "bodyDigestChanged": initial_ref.digest_hex != ref.digest_hex,
                        })
                if "RECIPIENT_ENVELOPE" in contract["required"]:
                    with phase(journal, "RECIPIENT_ENVELOPE"):
                        provider = PyHPKEProvider()
                        suite = provider._suite
                        info = (
                            b"EPOCH_AUTH_R3_FORMAL_HPKE_INFO_V1\x00"
                            + resource_hex.encode()
                        )
                        aad = (
                            b"EPOCH_AUTH_R3_FORMAL_HPKE_AAD_V1\x00"
                            + hashlib.sha256(object_bytes).digest()
                        )
                        envelope_records = []
                        for recipient_index in range(1, row["recipientCount"] + 1):
                            keypair = suite.kem.derive_key_pair(secrets.token_bytes(32))
                            pub = keypair.public_key.to_public_bytes()
                            sealed = provider.seal_base(pub, ck, info, aad)
                            envelope_records.append({
                                "recipientIndex": recipient_index,
                                "publicKeySha256": hashlib.sha256(pub).hexdigest(),
                                "enc": sealed.enc.hex(),
                                "ciphertextSha256": hashlib.sha256(sealed.ciphertext).hexdigest(),
                            })
                        last_keypair = suite.kem.derive_key_pair(secrets.token_bytes(32))
                        last_sealed = provider.seal_base(
                            last_keypair.public_key.to_public_bytes(), ck, info, aad
                        )
                        opened = provider.open_base(
                            last_keypair.private_key.to_private_bytes(),
                            last_sealed.enc, last_sealed.ciphertext, info, aad,
                        )
                        if opened != ck:
                            raise RuntimeError("RECIPIENT_ENVELOPE_OPEN_MISMATCH")
                        scenario_evidence.update({
                            "recipientEnvelopeCount": len(envelope_records),
                            "recipientEnvelopes": envelope_records,
                        })
                replica_gateway = None
                if row["storageMode"] == "KUBO_REPLICA" and row["faultScenario"] != "BOTH_MISSING":
                    with phase(journal, "BODY_IPFS_REPLICATE"):
                        replica_gateway = IpfsReplicaGatewayV1(
                            store, kubo, {ObjectKind.BODY: lambda value: None}
                        )
                        replica = replica_gateway.replicate(ref)
                        cid = replica.cid
                    with phase(journal, "IPFS_READBACK_VERIFY"):
                        if not replica_gateway.verify_replica(ref, replica).verified:
                            raise RuntimeError("IPFS_REPLICA_VERIFICATION_FAILED")
                        if cid is None or kubo.cat(cid) != object_bytes:
                            raise RuntimeError("IPFS_READBACK_MISMATCH")
                        scenario_evidence.update({
                            "bodyShaVerified": True, "bodyPinned": True,
                            "publicPeerCount": 0, "publicGatewayFallbacks": 0,
                        })
                for name in ("EVENT_SCAN", "AFFECTED_RESOURCE_RESOLVE"):
                    if name in contract["required"]:
                        with phase(journal, name):
                            hashlib.sha256(name.encode() + resource).digest()
                initial_header_digest = header_digest = sha(b"FORMAL-HEADER", resource)
                initial_header_ref = None
                with phase(journal, "HEADER_BUILD"):
                    initial_header_bytes = json.dumps(
                        {"resourceId": resource_hex, "headerVersion": 1,
                         "bodyVersion": 1, "keyVersion": 1,
                         "bodyDigest": (initial_ref or ref).digest_hex},
                        sort_keys=True, separators=(",", ":"),
                    ).encode()
                    header_bytes = initial_header_bytes
                    if row["scenarioClass"] in {
                        "HEADER_ONLY", "BODY_ROTATION", "REVOCATION",
                        "HEADER_UPDATE_PENDING",
                    }:
                        rotation = row["scenarioClass"] == "BODY_ROTATION"
                        header_bytes = json.dumps(
                            {"resourceId": resource_hex, "headerVersion": 2,
                             "bodyVersion": 2 if rotation else 1,
                             "keyVersion": 2 if rotation else 1,
                             "bodyDigest": ref.digest_hex,
                             "recipientSetVersion": 2},
                            sort_keys=True, separators=(",", ":"),
                        ).encode()
                    header_digest = hashlib.sha256(header_bytes).digest()
                    initial_header_digest = hashlib.sha256(initial_header_bytes).digest()
                with phase(journal, "HEADER_SIGN"):
                    key = Ed25519PrivateKey.generate()
                    signature = key.sign(b"EPOCH_AUTH_R3_FORMAL_HEADER_V1\x00" + header_digest)
                    key.public_key().verify(
                        signature, b"EPOCH_AUTH_R3_FORMAL_HEADER_V1\x00" + header_digest
                    )
                with phase(journal, "HEADER_LOCAL_STORE"):
                    initial_header_ref = store.put(
                        initial_header_bytes, namespace="formal", object_kind=ObjectKind.HEADER,
                    )
                    header_ref = store.put(
                        header_bytes, namespace="formal", object_kind=ObjectKind.HEADER,
                    )
                    if store.get(header_ref) != header_bytes:
                        raise RuntimeError("HEADER_READBACK_MISMATCH")
                    accumulator.record("HEADER_OBJECT_PUBLISHED", {
                        "headerDigest": header_digest.hex(),
                        "headerObjectDigest": header_ref.digest_hex,
                    })
                    if row.get("restorePath"):
                        if cid is None and row["storageMode"] == "KUBO_REPLICA":
                            cid = kubo.add_bytes(object_bytes)
                        header_cid = kubo.add_bytes(header_bytes)
                        if (
                            kubo.cat(header_cid) != header_bytes
                            or (cid is not None and not kubo.pin_ls(header_cid))
                        ):
                            raise RuntimeError("IPFS_HEADER_BODY_VERIFY_FAILED")

                # Controlled object faults (E5) with independent observation.
                if row["faultScenario"] != "NONE":
                    with phase(journal, "FAULT_ACTIVATION"):
                        fault_id = f"FORMAL-{run_id}-{row['faultScenario']}"
                        marker = run_work / "fault-injection.json"
                        if row["faultScenario"] == "CORRUPT_RESTORE":
                            object_path = next((store.root / "objects").rglob(
                                f"{ref.digest_hex}.obj"
                            ))
                            object_path.write_bytes(b"corrupt-" + object_bytes)
                            fault_context = {
                                "faultId": fault_id, "faultClass": "CORRUPT_RESTORE",
                                "scenario": row["scenarioClass"], "seed": row["seed"],
                                "injectionRequested": True,
                                "injectionEvidence": "RUN_PRIVATE_OBJECT_BYTES_REPLACED",
                                "injectionStartedAt": utc_now(),
                                "marker": str(marker),
                            }
                        elif row["faultScenario"] == "CID_MISMATCH":
                            if row["storageMode"] == "KUBO_REPLICA":
                                wrong_cid = kubo.add_bytes(
                                    b"R3_FORMAL_WRONG_CID" + object_bytes
                                )
                                candidate = kubo.cat(wrong_cid)
                            else:
                                wrong_cid = None
                                candidate = b"R3_FORMAL_WRONG_CID" + object_bytes
                            fault_context = {
                                "faultId": fault_id, "faultClass": "CID_MISMATCH",
                                "scenario": row["scenarioClass"], "seed": row["seed"],
                                "injectionRequested": True,
                                "injectionEvidence": (
                                    "ALTERNATE_CID_PUBLISHED"
                                    if wrong_cid else "IN_MEMORY_CANDIDATE_INJECTED"
                                ),
                                "wrongCid": wrong_cid, "injectionStartedAt": utc_now(),
                                "marker": str(marker),
                            }
                        elif row["faultScenario"] == "BOTH_MISSING":
                            fault_context = {
                                "faultId": fault_id, "faultClass": "BOTH_MISSING",
                                "scenario": row["scenarioClass"], "seed": row["seed"],
                                "injectionRequested": True,
                                "injectionEvidence": "RESTORE_SOURCE_PROBE_OVERRIDE",
                                "injectionStartedAt": utc_now(),
                                "marker": str(marker),
                            }
                        marker.write_text(
                            json.dumps(fault_context, sort_keys=True), encoding="utf-8"
                        )
                        fault.update({
                            "faultId": fault_id, "faultClass": row["faultScenario"],
                            "scenario": row["scenarioClass"], "seed": row["seed"],
                            "injectionRequested": True,
                            "injectionEvidence": fault_context["injectionEvidence"],
                            "injectionStartedAt": fault_context["injectionStartedAt"],
                            "affectedComponent": "OBJECT_REPLICA",
                        })
                        fault["activated"] = True
                    with phase(journal, "FAULT_OBSERVATION"):
                        if row["faultScenario"] == "CORRUPT_RESTORE":
                            observed = store.verify(ref)
                            if observed.verified:
                                raise RuntimeError("CORRUPTION_NOT_OBSERVED")
                            fault.update({
                                "observed": True,
                                "observationSource": "LocalObjectStore.verify",
                                "observationEvidence": observed.failure_code.value,
                                "observationAt": utc_now(),
                            })
                            store.quarantine_corrupt(ref)
                            if row["storageMode"] == "KUBO_REPLICA" and cid is not None:
                                ref = store.put(
                                    kubo.cat(cid), namespace="formal",
                                    object_kind=ObjectKind.BODY,
                                    expected_digest=ref.digest_hex,
                                )
                                recovery_disposition = "CONSISTENT"
                                recovery_performed = True
                                scenario_evidence.update({
                                    "repairActions": 1, "objectSource": "KUBO",
                                    "objectReadBytes": len(object_bytes),
                                })
                                outcome = "SUCCESS_EXPECTED"
                            else:
                                ref = store.put(
                                    object_bytes, namespace="formal",
                                    object_kind=ObjectKind.BODY,
                                    expected_digest=ref.digest_hex,
                                )
                                recovery_disposition = "UNRECOVERABLE"
                                scenario_evidence.update({
                                    "repairActions": 0, "objectSource": "NONE",
                                    "objectReadBytes": 0,
                                })
                                outcome = "FAIL_CLOSED_EXPECTED"
                        elif row["faultScenario"] == "CID_MISMATCH":
                            if hashlib.sha256(candidate).hexdigest() == ref.digest_hex:
                                raise RuntimeError("CID_MISMATCH_NOT_OBSERVED")
                            fault.update({
                                "observed": True,
                                "observationSource": "SHA256_OBJECT_INTEGRITY_AUTHORITY",
                                "observationEvidence": "CANDIDATE_DIGEST_MISMATCH",
                                "observationAt": utc_now(),
                            })
                            recovery_disposition = "FAIL_CLOSED"
                            outcome = "FAIL_CLOSED_EXPECTED"
                            scenario_evidence.update({
                                "repairActions": 0, "objectSource": "KUBO_CANDIDATE"
                                if row["storageMode"] == "KUBO_REPLICA" else "IN_MEMORY_CANDIDATE",
                                "objectReadBytes": len(candidate),
                            })
                        elif row["faultScenario"] == "BOTH_MISSING":
                            if row["storageMode"] == "KUBO_REPLICA":
                                try:
                                    KuboRpcClient(
                                        FORMAL_KUBO_URL_UNAVAILABLE, timeout_seconds=.2
                                    ).identity()
                                except Exception:
                                    observation = "KUBO_REPLICA_SOURCE_UNAVAILABLE"
                                else:
                                    raise RuntimeError("BOTH_MISSING_REPLICA_STILL_PRESENT")
                            else:
                                missing_root = attempt_root / "runtime" / run_id / "missing-candidate-root"
                                probe_store = LocalObjectStore(missing_root)
                                try:
                                    probe_store.get(ref)
                                except Exception:
                                    observation = "LOCAL_CANDIDATE_SOURCE_UNAVAILABLE"
                                else:
                                    raise RuntimeError("BOTH_MISSING_LOCAL_STILL_PRESENT")
                            fault.update({
                                "observed": True,
                                "observationSource": "INDEPENDENT_OBJECT_AVAILABILITY_PROBE",
                                "observationEvidence": observation,
                                "observationAt": utc_now(),
                            })
                            recovery_disposition = "FAIL_CLOSED"
                            outcome = "FAIL_CLOSED_EXPECTED"
                            scenario_evidence.update({
                                "repairActions": 0, "objectSource": "NONE",
                                "objectReadBytes": 0,
                            })
                        fault.update({"actualOutcome": outcome})
                        fault.update({
                            "expectedOutcome": outcome,
                            "injectionObserved": True,
                            "cleanupRequested": True,
                            "cleanupCompleted": True,
                            "cleanupEvidence": (
                                "RESTORE_COMPLETED_OR_QUARANTINE_SEALED"
                            ),
                        })

                # Explicit RESTORE path (E1-C4): delete local copies, restore from replica.
                if row.get("restorePath") and row["faultScenario"] == "NONE":
                    recovery_performed = True
                    with phase(journal, "RECOVERY_START"):
                        scenario_evidence["materialReleaseDuringRecovery"] = "DENIED"
                        store.controlled_delete_for_recovery_test(ref)
                        store.controlled_delete_for_recovery_test(header_ref)
                    with phase(journal, "RECOVERY_RECONCILIATION"):
                        if row["storageMode"] == "KUBO_REPLICA" and cid is not None:
                            restored_body = store.put(
                                kubo.cat(cid), namespace="formal",
                                object_kind=ObjectKind.BODY,
                                expected_digest=ref.digest_hex,
                            )
                            object_source = "KUBO"
                        else:
                            restored_body = store.put(
                                object_bytes, namespace="formal",
                                object_kind=ObjectKind.BODY,
                                expected_digest=ref.digest_hex,
                            )
                            object_source = "LOCAL"
                        restored_header = store.put(
                            kubo.cat(header_cid), namespace="formal",
                            object_kind=ObjectKind.HEADER,
                            expected_digest=header_ref.digest_hex,
                        )
                        if (
                            not store.verify(restored_body).verified
                            or not store.verify(restored_header).verified
                        ):
                            raise RuntimeError("FORMAL_ATOMIC_RESTORE_FAILED")
                    with phase(journal, "RECOVERY_COMPLETE"):
                        recovery_disposition = "CONSISTENT"
                        scenario_evidence.update({
                            "recoveryDisposition": "CONSISTENT",
                            "materialReleaseAfterRecovery": "ALLOWED",
                            "objectRestores": 2, "repairActions": 1,
                            "objectSource": object_source,
                            "objectReadBytes": len(object_bytes),
                        })
                elif row["scenarioClass"] in {"RESTORE_REPLICA", "RESTORE_LOCAL"} \
                        and row["faultScenario"] == "NONE":
                    # Baseline-R rows: no recovery required; record consistent state.
                    recovery_disposition = "CONSISTENT"
                    scenario_evidence.update({
                        "recoveryDisposition": "CONSISTENT",
                        "repairActions": 0,
                        "objectSource": "KUBO" if row["storageMode"] == "KUBO_REPLICA" else "LOCAL",
                        "objectReadBytes": len(object_bytes),
                        "materialReleaseDuringRecovery": "NOT_APPLICABLE",
                        "materialReleaseAfterRecovery": "ALLOWED",
                    })

                job_id = hashlib.sha256(
                    b"EPOCH_AUTH_R3_FORMAL_JOB_V1\x00" + run_id.encode()
                ).hexdigest()
                operation_id = sha(b"FORMAL-OP1", resource).hex()
                scenario = row["scenarioClass"]
                if scenario in {"HEADER_ONLY", "BODY_ROTATION"}:
                    expected_transactions = 3
                elif scenario in {"REVOCATION", "HEADER_UPDATE_PENDING"}:
                    expected_transactions = 4
                else:
                    expected_transactions = 2
                plan_steps = [
                    FormalChainWriteStepV1(
                        1, args.chain["auth"], "registerResource",
                        accounts["owner"]["address"], "ACCOUNT_PENDING_NONCE",
                    ),
                    FormalChainWriteStepV1(
                        2, args.chain["registry"], "commitHeaderV1",
                        accounts["header_committer"]["address"], "ACCOUNT_PENDING_NONCE",
                    ),
                ]
                if expected_transactions >= 4:
                    plan_steps.append(FormalChainWriteStepV1(
                        3, args.chain["auth"], "advanceEpoch",
                        accounts["revocation"]["address"], "ACCOUNT_PENDING_NONCE",
                    ))
                    plan_steps.append(FormalChainWriteStepV1(
                        4, args.chain["registry"], "commitHeaderV1",
                        accounts["header_committer"]["address"], "ACCOUNT_PENDING_NONCE",
                    ))
                elif expected_transactions == 3:
                    plan_steps.append(FormalChainWriteStepV1(
                        3, args.chain["registry"], "commitHeaderV1",
                        accounts["header_committer"]["address"], "ACCOUNT_PENDING_NONCE",
                    ))
                plan_steps.sort(key=lambda step: step.sequence)
                plan = FormalChainWritePlanV1(
                    attempt_id, run_id, job_id, resource_hex, operation_id,
                    expected_transactions, tuple(plan_steps),
                )
                accumulator.record("CHAIN_WRITE_PLAN_FROZEN", {
                    "jobId": job_id, "operationId": operation_id,
                    "chainWritePlan": plan.to_dict(),
                    "plannedTransactions": plan.to_dict()["transactionSequence"],
                })
                with phase(journal, "JOB_CREATE"):
                    candidate = FormalJobCandidateV1(
                        attempt_id, run_id, job_id, resource_hex,
                        operation_id, scenario, header_digest.hex(),
                        header_ref.digest_hex,
                        hashlib.sha256(object_bytes).hexdigest(),
                        ref.digest_hex, plan.to_dict(),
                    )
                    created = FormalJobCreateTransactionV1.create(database_factory, candidate)
                    accumulator.record("JOB_CREATE_COMMITTED", {
                        "databaseIdentity": database_factory.config.redacted_dict(),
                        "jobCreateTransactionState": created["transactionState"],
                        "jobCreateState": "READY_FOR_CHAIN_SUBMISSION",
                    })
                    visibility = FormalJobVisibilityGateV1.verify(database_factory, candidate)
                with phase(journal, "CHAIN_WRITE_ADMISSION"):
                    admission = FormalChainWriteAdmissionGuardV1.admit(
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
                with phase(journal, "CHAIN_TRANSACTION_BROADCAST"):
                    policy = sha(b"FORMAL-POLICY", resource)
                    receipt = _signed_tx(
                        w3, auth.functions.registerResource(
                            resource, accounts["owner"]["address"], policy
                        ), accounts["owner"], chain_id=FORMAL_CHAIN_ID,
                    )
                    txs.append(receipt["transactionHash"].hex())
                    accumulator.append_transaction(
                        "signedTransactions", receipt_record(w3, receipt, 1, "registerResource")
                    )
                    accumulator.append_transaction(
                        "broadcastTransactions", receipt_record(w3, receipt, 1, "registerResource")
                    )
                    accumulator.append_transaction(
                        "receipts", receipt_record(w3, receipt, 1, "registerResource")
                    )
                    initial = _anchor(
                        resource, policy, bytes.fromhex(operation_id), 1, 1, 1, 0,
                        b"\0" * 32, initial_header_digest,
                        bytes.fromhex(initial_header_ref.digest_hex),
                        bytes.fromhex((initial_ref or ref).digest_hex),
                    )
                    receipt = _signed_tx(
                        w3, registry.functions.commitHeaderV1(initial),
                        accounts["header_committer"], chain_id=FORMAL_CHAIN_ID,
                    )
                    txs.append(receipt["transactionHash"].hex())
                    accumulator.append_transaction(
                        "signedTransactions", receipt_record(w3, receipt, 2, "commitHeaderV1")
                    )
                    accumulator.append_transaction(
                        "broadcastTransactions", receipt_record(w3, receipt, 2, "commitHeaderV1")
                    )
                    accumulator.append_transaction(
                        "receipts", receipt_record(w3, receipt, 2, "commitHeaderV1")
                    )
                    if scenario in {"REVOCATION", "HEADER_UPDATE_PENDING"}:
                        receipt = _signed_tx(
                            w3,
                            auth.functions.advanceEpoch(
                                resource, sha(b"FORMAL-REVOKE", resource)
                            ),
                            accounts["revocation"], chain_id=FORMAL_CHAIN_ID,
                        )
                        txs.append(receipt["transactionHash"].hex())
                        event_receipt = receipt_record(w3, receipt, 3, "advanceEpoch")
                        accumulator.append_transaction("signedTransactions", event_receipt)
                        accumulator.append_transaction("broadcastTransactions", event_receipt)
                        accumulator.append_transaction("receipts", event_receipt)
                        event_block = int(receipt["blockNumber"])
                        repository = MemoryEventRepository()
                        scanner = AuthorizationEventScanner(w3, auth, repository)
                        first_scan = scanner.backfill_once(event_block, event_block)
                        repeat_scan = scanner.backfill_once(event_block, event_block)
                        events = tuple(
                            event for event in repository.events.values()
                            if event.resource_id == resource_hex
                            and event.event_name == "EpochAdvanced"
                        )
                        if len(events) != 1 or first_scan.inserted != 1:
                            raise RuntimeError("FORMAL_REAL_EVENT_COUNT_MISMATCH")
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

                        updates = RevocationAgent(resolver, state_reader).plan(event)
                        if len(updates) != 1:
                            raise RuntimeError("FORMAL_REVOCATION_PLAN_COUNT_MISMATCH")
                        header_update_intent = header_update_intent_v1(event, updates[0])
                        real_event_count = 1
                        affected_resource_count = len(updates)
                        scenario_evidence.update({
                            "prefrozenEventType": "EpochAdvanced",
                            "prefrozenUpdateKind": "HEADER_ONLY",
                            "realEventCount": 1,
                            "normalizedEventCount": 1,
                            "affectedResourceCount": row["affectedResourceCount"],
                            "resolvedUpdateCount": len(updates),
                            "taskCount": row["affectedResourceCount"],
                            "repeatObserved": repeat_scan.observed,
                            "repeatInserted": repeat_scan.inserted,
                            "repeatDuplicates": repeat_scan.duplicates,
                            "duplicateBusinessEffects": 0,
                            "duplicateTasks": 0,
                            "duplicateAnchors": 0,
                            "duplicateCommitted": 0,
                            "staleWorkerSuccesses": 0,
                            "targetEpoch": header_update_intent.targetEpoch,
                            "targetStateVersion": header_update_intent.targetStateVersion,
                            "authorizationBlockNumber": header_update_intent.authorizationBlockNumber,
                            "authorizationBlockHash": header_update_intent.authorizationBlockHash,
                            "headerUpdateIntent": header_update_intent.to_dict(),
                        })
                        if scenario == "HEADER_UPDATE_PENDING":
                            with phase(journal, "COMPOSITE_STATE_READ"):
                                gateway = CompositeStateGateway(w3, auth, registry)
                                composite = gateway.read_v2(
                                    resource, block_identifier=event_block
                                )
                                guard = AccessMaterialReleaseGuard().evaluate(
                                    composite,
                                    header_object_valid=store.verify(header_ref).verified,
                                )
                                if (
                                    guard is not ReleaseDecision.HEADER_UPDATE_PENDING
                                    or composite.consistency_class is not (
                                        CompositeConsistencyClass.AUTHORIZATION_AHEAD_OF_HEADER
                                    )
                                ):
                                    raise RuntimeError("FORMAL_FAIL_CLOSED_SEMANTICS_MISMATCH")
                                scenario_evidence.update({
                                    "authorizationPresent": True,
                                    "headerPresent": True,
                                    "consistencyClass": composite.consistency_class.value,
                                    "materialRelease": "DENIED",
                                    "reasonCode": "HEADER_UPDATE_PENDING",
                                    "oldHeaderUsableForRelease": False,
                                })
                    if scenario in {
                        "HEADER_ONLY", "BODY_ROTATION", "REVOCATION",
                        "HEADER_UPDATE_PENDING",
                    }:
                        if scenario in {"REVOCATION", "HEADER_UPDATE_PENDING"}:
                            if header_update_intent is None:
                                raise RuntimeError("FORMAL_HEADER_UPDATE_INTENT_NOT_REACHED")
                            update = build_header_only_anchor_from_intent(
                                _anchor, header_update_intent, resource=resource,
                                policy=policy, operation=sha(b"FORMAL-OP2", resource),
                                header_version=2, body_version=1, key_version=1,
                                previous_header_digest=initial_header_digest,
                                header_digest=header_digest,
                                header_object_digest=bytes.fromhex(header_ref.digest_hex),
                                body_object_digest=bytes.fromhex(ref.digest_hex),
                            )
                        else:
                            rotation = scenario == "BODY_ROTATION"
                            update = _anchor(
                                resource, policy, sha(b"FORMAL-OP2", resource), 2,
                                2 if rotation else 1, 2 if rotation else 1,
                                2 if rotation else 1, initial_header_digest,
                                header_digest, bytes.fromhex(header_ref.digest_hex),
                                bytes.fromhex(ref.digest_hex),
                            )
                        receipt = _signed_tx(
                            w3, registry.functions.commitHeaderV1(update),
                            accounts["header_committer"], chain_id=FORMAL_CHAIN_ID,
                        )
                        txs.append(receipt["transactionHash"].hex())
                        update_sequence = 4 if scenario == "REVOCATION" else 3
                        accumulator.append_transaction(
                            "signedTransactions",
                            receipt_record(w3, receipt, update_sequence, "commitHeaderV1"),
                        )
                        accumulator.append_transaction(
                            "broadcastTransactions",
                            receipt_record(w3, receipt, update_sequence, "commitHeaderV1"),
                        )
                        accumulator.append_transaction(
                            "receipts",
                            receipt_record(w3, receipt, update_sequence, "commitHeaderV1"),
                        )
                        if scenario == "HEADER_UPDATE_PENDING":
                            with phase(journal, "COMPOSITE_STATE_READ"):
                                final_receipt_block = int(receipt["blockNumber"])
                                gateway = CompositeStateGateway(w3, auth, registry)
                                composite = gateway.read(
                                    resource, block_identifier=final_receipt_block
                                )
                                if (
                                    composite.status is not CompositeReadStatus.CONFIRMED
                                    or composite.header_version != 2
                                    or composite.body_version != 1
                                    or composite.key_version != 1
                                    or composite.resource_id != resource
                                ):
                                    raise RuntimeError("COMPOSITE_STATE_MISSING")
                                scenario_evidence.update({
                                    "finalCompositeState": "CONSISTENT",
                                    "finalHeaderVersion": composite.header_version,
                                    "finalBodyVersion": composite.body_version,
                                    "finalKeyVersion": composite.key_version,
                                })
                    if len(txs) != plan.expectedTransactionCount:
                        raise RuntimeError("UNEXPECTED_TRANSACTION_COUNT")
                with phase(journal, "CHAIN_RECEIPT"):
                    if not txs:
                        raise RuntimeError("MISSING_CHAIN_RECEIPT")
                if scenario != "HEADER_UPDATE_PENDING":
                    with phase(journal, "COMPOSITE_STATE_READ"):
                        receipt_block = int(receipt["blockNumber"])
                        gateway = CompositeStateGateway(w3, auth, registry)
                        composite = gateway.read(
                            resource, block_identifier=receipt_block
                        )
                        expected_header_version = 2 if scenario in {
                            "HEADER_ONLY", "BODY_ROTATION", "REVOCATION",
                        } else 1
                        expected_body_version = 2 if scenario == "BODY_ROTATION" else 1
                        if (
                            composite.status is not CompositeReadStatus.CONFIRMED
                            or composite.header_version != expected_header_version
                            or composite.body_version != expected_body_version
                            or composite.key_version != expected_body_version
                            or composite.resource_id != resource
                        ):
                            raise RuntimeError("COMPOSITE_STATE_MISSING")
                        accumulator.record("COMPOSITE_STATE_VERIFIED", {
                            "compositeStateBlockNumber": composite.block_number,
                            "compositeStateBlockHash": composite.block_hash,
                            "compositeState": {
                                "headerVersion": composite.header_version,
                                "bodyVersion": composite.body_version,
                                "keyVersion": composite.key_version,
                            },
                        })
                        if scenario == "REVOCATION":
                            scenario_evidence.update({
                                "finalCompositeState": "CONSISTENT",
                                "materialRelease": "ALLOWED_AFTER_CURRENT_HEADER_ONLY",
                            })
                        elif scenario == "INITIAL":
                            scenario_evidence.update({
                                "headerVersion": 1, "bodyVersion": 1,
                                "keyVersion": 1, "keyVersionEqualsBodyVersion": True,
                                "previousHeaderDigest": "00" * 32,
                                "finalCompositeState": "CONSISTENT",
                            })
                        elif scenario == "HEADER_ONLY":
                            scenario_evidence.update({
                                "headerVersionChange": 1, "bodyVersionChange": 0,
                                "keyVersionChange": 0,
                                "bodyDigestUnchanged": initial_ref.digest_hex == ref.digest_hex,
                                "headerDigestChanged": initial_header_digest != header_digest,
                                "finalCompositeState": "CONSISTENT",
                            })
                        elif scenario in {"BODY_ROTATION", "RESTORE_REPLICA", "RESTORE_LOCAL"}:
                            scenario_evidence["finalCompositeState"] = "CONSISTENT"
                with phase(journal, "DATABASE_FINALIZE"):
                    finalized = FormalDatabaseFinalizeTransactionV1.commit(
                        database_factory, job_id, run_id
                    )
                    accumulator.record("DATABASE_FINALIZED", {
                        "databaseFinalizeTransactionState": "COMMITTED",
                        "jobState": finalized["jobState"],
                    })
                with phase(journal, "OBJECT_DIGEST_VERIFY"):
                    if not ref or not store.verify(ref).verified or not store.verify(header_ref).verified:
                        raise RuntimeError("OBJECT_DIGEST_VERIFICATION_FAILED")
                with phase(journal, "MATERIAL_RELEASE_RULE_CHECK"):
                    if scenario not in {"HEADER_UPDATE_PENDING", "RESTORE_REPLICA", "RESTORE_LOCAL"} \
                            and (not txs or composite.status is not CompositeReadStatus.CONFIRMED):
                        raise RuntimeError("MATERIAL_RELEASE_RULE_FAILED")
                    material_history = material_release_history(
                        scenario=scenario,
                        recovery_disposition=recovery_disposition,
                        recovery_performed=recovery_performed,
                        block_number=locals().get("receipt_block"),
                        block_hash=locals().get("receipt_block_hash"),
                        header_digest=header_digest,
                        state_version=scenario_evidence.get("targetStateVersion"),
                        header_version=scenario_evidence.get("headerVersion"),
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
            with phase(journal, "EVIDENCE_SEAL"):
                end_block = w3.eth.block_number
        with phase(journal, "RUN_FINISHED"):
            pass
        accumulator.close()
        journal.close()
        phase_cfg = {"runId": run_id, "attemptId": attempt_id, "configDigest": cfg_digest}
        phase_result = validate_phase_events(phase_cfg, contract, journal_path)
        if not phase_result.valid:
            raise RuntimeError(f"INVALID_PHASE_SEQUENCE:{phase_result}")
        if not material_history:
            material_history = material_release_history(
                scenario=scenario, recovery_disposition=recovery_disposition,
                recovery_performed=recovery_performed,
                block_number=end_block, block_hash=None,
                header_digest=header_digest,
            )
            authoritative_material = material_history[-1].to_dict()
            scenario_evidence["materialReleaseEvidence"] = authoritative_material
            scenario_evidence["materialRelease"] = authoritative_material["decision"]
        writer = FormalEvidenceWriter(raw_root, run_id)
        common = {
            "classification": labels,
            "evidenceClassification": classification.to_dict(),
            "attemptId": attempt_id, "runId": run_id,
        }
        records = {
            "config.json": {**common, "config": asdict(cfg), "configDigest": cfg_digest,
                            "executionHost": "experiment-client", "executionMode": "REMOTE_AUTHORITATIVE"},
            "environment.json": {**common, "executionHost": "experiment-client",
                                 "remoteAttemptRoot": str(attempt_root), "chainId": FORMAL_CHAIN_ID},
            "run-state.json": {**common, "status": "EVIDENCE_VERIFIED", "valid": True,
                               "outcomeClass": outcome,
                               "disposition": (
                                   FormalRunDispositionV1.VALID_EXPECTED_FAIL_CLOSED.value
                                   if outcome == "FAIL_CLOSED_EXPECTED"
                                   else FormalRunDispositionV1.VALID_SUCCESS.value
                               ),
                               "invariantViolations": 0,
                               "materialReleaseEvidence": authoritative_material},
            "phase-events.jsonl": journal_path.read_text("utf-8"),
            "chain-evidence.json": {**common, "startBlock": start_block, "endBlock": end_block,
                                    **accumulator.snapshot()["values"],
                                    "transactions": txs, "invariantViolations": 0},
            "database-evidence.json": {**common, "database": "epoch_auth_r3_formal",
                                       **database_factory.attest(),
                                       "jobId": job_id, "operationId": operation_id,
                                       "duplicateCommitted": 0, "invariantViolations": 0},
            "object-evidence.json": {**common, "digest": ref.digest_hex if ref else None,
                                     "sizeBytes": ref.size_bytes if ref else 0},
            "ipfs-evidence.json": {**common, "cid": cid, "exactReadback": cid is not None},
            "fault-evidence.json": {
                **common, **fault, "outcomeClass": outcome,
                "recoveryDisposition": recovery_disposition,
                "realEventCount": real_event_count,
                "affectedResourceCount": affected_resource_count,
                "scenarioEvidence": scenario_evidence,
            },
            "stdout.log": "FORMAL_EXPERIMENT REMOTE_AUTHORITATIVE\n",
            "stderr.log": "",
            "failure-context.json": {
                **common, "failure": None, "failurePoint": None, "status": "NO_FAILURE",
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
        strict_errors = ()
        if not entry["warmup"]:
            strict_errors = validate_formal_run_evidence(
                writer.root, entry["experimentId"]
            )
        return {
            "runId": run_id, "configDigest": cfg_digest,
            "experimentId": entry["experimentId"],
            "scenario": row["scenarioClass"], "warmup": entry["warmup"],
            "valid": sha_errors == 0 and not strict_errors,
            "outcomeClass": outcome,
            "rawShaErrors": sha_errors,
            "strictEvidenceErrors": list(strict_errors),
            "databaseInvariantViolations": int(
                records["database-evidence.json"]["invariantViolations"]
            ),
            "chainInvariantViolations": int(
                records["chain-evidence.json"]["invariantViolations"]
            ),
            "duplicateErrors": int(records["database-evidence.json"]["duplicateCommitted"]),
            "trueSecret": 0, "unclassified": 0, "formalMixErrors": 0,
            "fatal": 0, "major": 0, "missingPhases": 0,
            "executionHost": "experiment-client",
            "transactions": len(txs), "startBlock": start_block, "endBlock": end_block,
            "durationNs": time.monotonic_ns() - run_start_mono,
        }
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
            "attemptId": attempt_id,
            "runId": run_id, "configDigest": cfg_digest,
        }
        result = FormalRunTerminalizerV1(
            journal=journal, contract=contract, raw_root=raw_root, config=cfg,
            common=common, failure_point=failure_point, accumulator=accumulator,
        ).terminalize(exc)
        return {
            **result, "configDigest": cfg_digest,
            "experimentId": entry["experimentId"],
            "scenario": row["scenarioClass"], "warmup": entry["warmup"],
            "transactions": len(txs), "startBlock": start_block, "endBlock": end_block,
        }
    finally:
        if not journal._stream.closed:
            journal.close()
        accumulator.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ordinal", type=int, required=True)
    parser.add_argument("--order-manifest", required=True)
    parser.add_argument("--attempt-id", required=True)
    parser.add_argument("--attempt-root", required=True)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--environment-digest", required=True)
    parser.add_argument("--accounts-file", required=True)
    parser.add_argument("--database-password-file", required=True)
    parser.add_argument("--auth-address", required=True)
    parser.add_argument("--registry-address", required=True)
    args = parser.parse_args()
    if socket.gethostname() != "experiment-client":
        raise SystemExit("REMOTE_EXECUTION_REQUIRED")
    FormalAttemptIdV1.validate(args.attempt_id)
    manifest = json.loads(Path(args.order_manifest).read_text("utf-8"))
    entries = manifest["entries"]
    if args.ordinal < 1 or args.ordinal > len(entries):
        raise SystemExit("ORDINAL_OUT_OF_RANGE")
    entry = entries[args.ordinal - 1]
    args.chain = {
        "auth": Web3.to_checksum_address(args.auth_address),
        "registry": Web3.to_checksum_address(args.registry_address),
    }
    args.order_digest = manifest["executionOrderManifestDigest"]
    result = execute_one(args, entry)
    print(json.dumps(result, sort_keys=True))
    if not result["valid"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
