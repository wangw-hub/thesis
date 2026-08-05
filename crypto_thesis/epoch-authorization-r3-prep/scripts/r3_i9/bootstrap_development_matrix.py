"""Atomically bootstrap one DEVELOPMENT_ONLY full-matrix root."""
from __future__ import annotations

import argparse
import hashlib
import json
import socket
from datetime import datetime, timezone
from pathlib import Path

from epoch_auth_r3.pilot.bootstrap import AtomicJsonWriterV1


def bootstrap(root: Path, dev_id: str, commit: str, pilot_root: Path) -> dict:
    if socket.gethostname() != "experiment-client":
        raise RuntimeError("REMOTE_EXECUTION_REQUIRED")
    if root.exists() or not dev_id.startswith("DEV_P9A_"):
        raise RuntimeError("DEVELOPMENT_ROOT_OR_ID_INVALID")
    root.mkdir(parents=True, exist_ok=False)
    for name in ("manifests", "runtime", "raw", "state", "local-store"):
        (root / name).mkdir()
    old_ids = sorted({
        item.name
        for base in (
            *pilot_root.glob("attempts/*/raw"),
            *(pilot_root.parent / "i9-development").rglob("raw"),
        )
        if base.is_dir()
        for item in base.iterdir()
        if item.is_dir()
    })
    environment = {
        "schemaVersion": "R3DevelopmentEnvironmentV1",
        "developmentId": dev_id,
        "executionHost": "experiment-client",
        "databaseHost": "127.0.0.1",
        "databasePort": 55432,
        "database": "epoch_auth_r3_i9_pilot",
        "chainId": 2026073005,
        "rpc": "127.0.0.1:18545",
        "kuboApi": "127.0.0.1:15001",
        "softwareCommit": commit,
        "classification": [
            "DEVELOPMENT_ONLY", "NOT_PILOT_EVIDENCE",
            "NOT_FOR_STATISTICS", "NOT_FOR_THESIS_RESULTS",
        ],
    }
    digest = hashlib.sha256(json.dumps(
        environment, sort_keys=True, separators=(",", ":")
    ).encode()).hexdigest()
    AtomicJsonWriterV1.write(root / "manifests/environment.json", environment)
    AtomicJsonWriterV1.write(root / "manifests/old-run-ids.json", old_ids)
    AtomicJsonWriterV1.write(root / "manifests/development-bootstrap.json", {
        "schemaVersion": "R3DevelopmentBootstrapV1",
        "developmentId": dev_id,
        "softwareCommit": commit,
        "environmentManifestDigest": digest,
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "state": "DEVELOPMENT_READY",
        "oldRunIdCount": len(old_ids),
    })
    AtomicJsonWriterV1.write(root / "state/stage-gate-state.json", {
        "state": "DEVELOPMENT_READY", "history": [],
    })
    return {"developmentId": dev_id, "environmentDigest": digest,
            "oldRunIdCount": len(old_ids), "root": str(root)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--development-id", required=True)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--pilot-root", type=Path, default=Path("/var/lib/epoch-auth-r3/i9-pilot"))
    args = parser.parse_args()
    print(json.dumps(bootstrap(args.root, args.development_id, args.commit, args.pilot_root), sort_keys=True))


if __name__ == "__main__":
    main()
