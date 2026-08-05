"""Atomically create one immutable final P9-A attempt after readiness approval."""
from __future__ import annotations

import argparse
import hashlib
import json
import socket
from datetime import UTC, datetime
from pathlib import Path

from epoch_auth_r3.pilot.attempt import PilotAttemptIdV1
from epoch_auth_r3.pilot.bootstrap import AtomicJsonWriterV1


CLASSIFICATION = [
    "PILOT_ONLY", "P9_A_SMOKE_ONLY",
    "NOT_FOR_FORMAL_THESIS_RESULTS", "NOT_FOR_PERFORMANCE_CLAIMS",
]


def bootstrap(pilot_root: Path, commit: str, archive_sha256: str, *, stage: str = "P9-A") -> dict:
    if socket.gethostname() != "experiment-client":
        raise RuntimeError("REMOTE_EXECUTION_REQUIRED")
    if len(commit) != 40 or len(archive_sha256) != 64:
        raise ValueError("INVALID_FROZEN_CODE_IDENTITY")
    stage_spec = {
        "P9-A": ("P9A", "FINAL_P9A_SMOKE_ONLY", 8, "P9_A_READY", "CANARY_PASSED"),
        "P9-B": ("P9B", "P9_B_UPDATE_PATH_PILOT", 45, "P9_A_PASSED", "CANARY_PASSED"),
        "P9-C": ("P9C", "P9_C_STORAGE_RECOVERY_PILOT", 16, "P9_B_PASSED", "CANARY_PASSED"),
        "P9-D": ("P9D", "P9_D_FAULT_RECOVERY_PILOT", 24, "P9_C_PASSED", "CANARY_PASSED"),
    }
    try:
        family, purpose, planned, initial_state, canary = stage_spec[stage]
    except KeyError as exc:
        raise ValueError("UNKNOWN_PILOT_STAGE") from exc
    classification = ["PILOT_ONLY", stage.replace("-", "_"),
                      "NOT_FOR_FORMAL_THESIS_RESULTS", "NOT_FOR_PERFORMANCE_CLAIMS"]
    if stage == "P9-A":
        classification[1] = "P9_A_SMOKE_ONLY"
    attempt = PilotAttemptIdV1.create(family=family, created_at=datetime.now(UTC), git_sha=commit)
    attempt_id = attempt.serialize()
    if PilotAttemptIdV1.parse(attempt_id).serialize() != attempt_id or PilotAttemptIdV1.validate(attempt_id) != attempt:
        raise RuntimeError("ATTEMPT_ID_ROUND_TRIP_FAILED")
    root = pilot_root / "attempts" / attempt_id
    root.mkdir(parents=False, exist_ok=False)
    for name in ("manifests", "runtime", "raw", "state", "local-store"):
        (root / name).mkdir()
    identity_roots = [pilot_root / "attempts", pilot_root.parent / "i9-development"]
    old_run_ids = sorted({
        item.name for identity_root in identity_roots if identity_root.is_dir()
        for raw in identity_root.rglob("raw") if raw != root / "raw"
        for item in raw.iterdir() if item.is_dir()
    })
    environment = {
        "schemaVersion": 1, "executionHost": "experiment-client",
        "database": "epoch_auth_r3_i9_pilot", "databaseHost": "127.0.0.1", "databasePort": 55432,
        "chainId": 2026073005, "rpc": "127.0.0.1:18545",
        "authorizationState": "0x12BA996711Db58897A525b5a718225bD085A3c5f",
        "headerRegistry": "0x280b757a16525AdAef8ED88EE158e0c6F924B35F",
        "kuboApi": "127.0.0.1:15001", "softwareCommit": commit,
        "remoteCodeSnapshotSha256": archive_sha256, "classification": classification,
    }
    environment_digest = hashlib.sha256(
        json.dumps(environment, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    AtomicJsonWriterV1.write(root / "manifests/environment.json", environment)
    AtomicJsonWriterV1.write(root / "manifests/old-run-ids.json", old_run_ids)
    AtomicJsonWriterV1.write(root / "manifests/attempt-bootstrap-manifest.json", {
        "schemaVersion": 1, "attemptId": attempt_id, "attemptPurpose": purpose,
        "softwareCommit": commit, "remoteCodeSnapshotSha256": archive_sha256,
        "environmentManifestDigest": environment_digest, "createdAt": datetime.now(UTC).isoformat(),
        "bootstrapState": "PUBLISHED", "attemptIdRoundTrip": "PASSED", "classification": classification,
        "plannedRuns": planned, "stage": stage,
    })
    AtomicJsonWriterV1.write(root / "state/stage-gate-state.json", {
        "schemaVersion": 1, "attemptId": attempt_id, "canary": canary,
        "state": initial_state, "history": [{"stage": f"{stage}_BOOTSTRAP", "transition": initial_state}],
    })
    return {"attemptId": attempt_id, "attemptRoot": str(root),
            "environmentDigest": environment_digest, "oldRunIdCount": len(old_run_ids)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot-root", type=Path, default=Path("/var/lib/epoch-auth-r3/i9-pilot"))
    parser.add_argument("--commit", required=True)
    parser.add_argument("--archive-sha256", required=True)
    parser.add_argument("--stage", choices=("P9-A", "P9-B", "P9-C", "P9-D"), default="P9-A")
    args = parser.parse_args()
    print(json.dumps(bootstrap(args.pilot_root, args.commit, args.archive_sha256, stage=args.stage), sort_keys=True))


if __name__ == "__main__":
    main()
