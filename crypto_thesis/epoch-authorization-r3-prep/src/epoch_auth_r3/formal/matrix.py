from __future__ import annotations

import hashlib
import json
import random
from datetime import datetime, timezone
from dataclasses import dataclass
from pathlib import Path

from epoch_auth_r3.formal.config import R3FormalConfigV1, config_digest
from epoch_auth_r3.formal.classification import FormalEvidenceClassificationV1


ORDER_DOMAIN = b"EPOCH_AUTH_R3_FORMAL_ORDER_V1\x00"
FORMAL_SEED = 20260802
FORMAL_CHAIN_ID = 2026080201
FORMAL_KUBO_URL = "http://127.0.0.1:15998"


@dataclass(frozen=True)
class FormalMatrixRowV1:
    experimentId: str
    configIndex: int
    scenarioClass: str
    semanticClass: str
    workloadType: str
    bodySizeBytes: int
    recipientCount: int
    affectedResourceCount: int
    storageMode: str
    faultScenario: str
    seed: int
    workerCount: int = 1
    restorePath: bool = False

    def to_dict(self) -> dict:
        return {
            "experimentId": self.experimentId,
            "configIndex": self.configIndex,
            "scenarioClass": self.scenarioClass,
            "semanticClass": self.semanticClass,
            "workloadType": self.workloadType,
            "bodySizeBytes": self.bodySizeBytes,
            "recipientCount": self.recipientCount,
            "affectedResourceCount": self.affectedResourceCount,
            "storageMode": self.storageMode,
            "faultScenario": self.faultScenario,
            "seed": self.seed,
            "workerCount": self.workerCount,
            "restorePath": self.restorePath,
        }

    @classmethod
    def from_dict(cls, value: dict) -> "FormalMatrixRowV1":
        return cls(**value)


def _e1() -> list[FormalMatrixRowV1]:
    rows = []
    for index, spec in enumerate((
        ("INITIAL", "INITIAL", "HEADER_UPDATE", 701),
        ("BODY_ROTATION", "BODY_ROTATION", "BODY_ROTATION", 702),
        ("REVOCATION", "REVOCATION", "REVOCATION", 703),
        ("RESTORE_REPLICA", "RESTORE", "RESTORE", 704),
    ), start=1):
        scenario, semantic, workload, seed = spec
        rows.append(FormalMatrixRowV1(
            "E1", index, scenario, semantic, workload, 65536, 2, 1,
            "LOCAL_ONLY" if scenario != "RESTORE_REPLICA" else "KUBO_REPLICA",
            "NONE", seed, restorePath=(scenario == "RESTORE_REPLICA"),
        ))
    return rows


def _e2() -> list[FormalMatrixRowV1]:
    rows = []
    index = 0
    for recipients in (2, 8, 32):
        for affected in (1, 4):
            index += 1
            rows.append(FormalMatrixRowV1(
                "E2", index, "HEADER_ONLY", "HEADER_ONLY", "HEADER_UPDATE",
                65536, recipients, affected, "LOCAL_ONLY", "NONE", 800 + index,
            ))
    return rows


def _e3() -> list[FormalMatrixRowV1]:
    rows = []
    index = 0
    for size in (65536, 1048576, 8388608):
        for recipients in (2, 8, 32):
            index += 1
            rows.append(FormalMatrixRowV1(
                "E3", index, "BODY_ROTATION", "BODY_ROTATION", "BODY_ROTATION",
                size, recipients, 1, "LOCAL_ONLY", "NONE", 900 + index,
            ))
    return rows


def _e4() -> list[FormalMatrixRowV1]:
    return [
        FormalMatrixRowV1("E4", 1, "REVOCATION", "REVOCATION", "REVOCATION",
                          65536, 2, 1, "LOCAL_ONLY", "NONE", 1001),
        FormalMatrixRowV1("E4", 2, "HEADER_UPDATE_PENDING", "REVOCATION", "REVOCATION",
                          65536, 2, 1, "LOCAL_ONLY", "NONE", 1002),
    ]


def _e5() -> list[FormalMatrixRowV1]:
    rows = []
    index = 0
    for replica in ("LOCAL_ONLY", "KUBO_REPLICA"):
        for fault, seed in (
            ("NONE", 1101), ("CORRUPT_RESTORE", 1102),
            ("CID_MISMATCH", 1103), ("BOTH_MISSING", 1104),
        ):
            index += 1
            scenario = "RESTORE_REPLICA" if replica == "KUBO_REPLICA" else "RESTORE_LOCAL"
            rows.append(FormalMatrixRowV1(
                "E5", index, scenario, "RESTORE", "RESTORE",
                65536, 2, 1, replica, fault, seed, restorePath=(fault != "NONE"),
            ))
    return rows


def measured_matrix() -> list[FormalMatrixRowV1]:
    return _e1() + _e2() + _e3() + _e4() + _e5()


def warmup_matrix() -> list[FormalMatrixRowV1]:
    """29 per-config warmups (one per measured config) + 6 environment warmups."""
    rows = []
    for measured in measured_matrix():
        rows.append(FormalMatrixRowV1(
            "WARMUP", measured.configIndex, measured.scenarioClass,
            measured.semanticClass, measured.workloadType,
            measured.bodySizeBytes, measured.recipientCount,
            measured.affectedResourceCount, measured.storageMode,
            measured.faultScenario, 20000 + measured.seed,
        ))
    for env_index in range(1, 7):
        rows.append(FormalMatrixRowV1(
            "WARMUP", 100 + env_index, "INITIAL", "INITIAL", "ENVIRONMENT_WARMUP",
            4096, 2, 1, "LOCAL_ONLY", "NONE", 25000 + env_index,
        ))
    return rows


def config_digest_for_row(row: FormalMatrixRowV1, *, attempt_id: str,
                          software_commit: str, env_digest: str,
                          warmup: bool, repeat_index: int,
                          chain: dict, attempt_root: str) -> str:
    cfg = formal_config_for_entry(
        row=row, attempt_id=attempt_id, commit=software_commit,
        env_digest=env_digest, warmup=warmup, repeat_index=repeat_index,
        chain=chain, attempt_root=attempt_root,
    )
    return config_digest(cfg)


def formal_config_for_entry(
    *, row: FormalMatrixRowV1 | dict, attempt_id: str, commit: str,
    env_digest: str, warmup: bool, repeat_index: int,
    chain: dict, attempt_root: str,
) -> R3FormalConfigV1:
    row = row if isinstance(row, FormalMatrixRowV1) else FormalMatrixRowV1.from_dict(row)
    classification = FormalEvidenceClassificationV1.for_config(
        experiment_id=row.experimentId, scenario_class=row.scenarioClass,
        semantic_class=row.semanticClass,
    )
    workload_id = (
        f"R3_FORMAL_{row.experimentId}_{row.configIndex:03d}_"
        f"{'W' if warmup else 'M'}{repeat_index}"
    )
    return R3FormalConfigV1(
        1, "R3_FORMAL_V1", row.experimentId, row.seed, workload_id,
        row.scenarioClass, row.semanticClass,
        row.bodySizeBytes, row.recipientCount, row.affectedResourceCount, 1,
        row.storageMode, row.faultScenario,
        repeat_index, warmup, not warmup,
        FORMAL_CHAIN_ID, chain["auth"], chain["registry"], "epoch_auth_r3_formal",
        attempt_root + "/local-store", FORMAL_KUBO_URL, "formal-kubo-profile",
        commit, env_digest,
        datetime.now(timezone.utc).isoformat(),
        evidenceClassification=classification.to_dict(),
    )


def build_execution_order(*, attempt_id: str, software_commit: str,
                          env_digest: str, chain: dict,
                          seed: int = FORMAL_SEED) -> dict:
    """Blocked deterministic randomization; repetitions run consecutively per config."""
    entries = []
    warmups = warmup_matrix()
    measured = measured_matrix()
    rng = random.Random(seed)
    warmup_configs = [row for row in warmups if row.configIndex < 100]
    env_warmups = [row for row in warmups if row.configIndex >= 100]
    rng.shuffle(warmup_configs)
    rng.shuffle(env_warmups)
    blocks = [
        ("WARMUP", warmup_configs + env_warmups, True),
    ]
    for experiment_id in ("E1", "E2", "E3", "E4", "E5"):
        configs = [row for row in measured if row.experimentId == experiment_id]
        rng.shuffle(configs)
        blocks.append((experiment_id, configs, False))

    # Compute order digest from the deterministic block structure first.
    def run_entries() -> list[dict]:
        produced = []
        ordinal = 0
        for block_name, configs, warmup in blocks:
            for row in configs:
                repeats = 1 if warmup else 5
                for repeat in range(1, repeats + 1):
                    ordinal += 1
                    produced.append({
                        "ordinal": ordinal,
                        "block": block_name,
                        "experimentId": row.experimentId,
                        "configIndex": row.configIndex,
                        "repeatIndex": repeat,
                        "warmup": warmup,
                        "row": row.to_dict(),
                    })
        return produced

    entries = run_entries()
    attempt_root = f"/var/lib/epoch-auth-r3/formal/attempts/{attempt_id}"
    for entry in entries:
        row = FormalMatrixRowV1.from_dict(entry.pop("row"))
        entry["row"] = row.to_dict()
        entry["configDigest"] = config_digest_for_row(
            row, attempt_id=attempt_id, software_commit=software_commit,
            env_digest=env_digest, warmup=entry["warmup"],
            repeat_index=entry["repeatIndex"], chain=chain,
            attempt_root=attempt_root,
        )
        entry["runId"] = hashlib.sha256(
            b"EPOCH_AUTH_R3_FORMAL_RUN_ATTEMPT_V1\x00"
            + attempt_id.encode("ascii")
            + bytes.fromhex(entry["configDigest"])
        ).hexdigest()
    final_digest = hashlib.sha256(
        ORDER_DOMAIN + json.dumps(entries, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return {
        "schemaVersion": "FormalExecutionOrderManifestV1",
        "randomization": {"strategy": "blocked deterministic randomization", "seed": seed},
        "attemptId": attempt_id,
        "softwareCommit": software_commit,
        "environmentManifestDigest": env_digest,
        "executionOrderManifestDigest": final_digest,
        "warmupCount": sum(1 for entry in entries if entry["warmup"]),
        "measuredCount": sum(1 for entry in entries if not entry["warmup"]),
        "totalRuns": len(entries),
        "entries": entries,
    }


def write_manifest(path: Path, manifest: dict) -> str:
    path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return manifest["executionOrderManifestDigest"]
