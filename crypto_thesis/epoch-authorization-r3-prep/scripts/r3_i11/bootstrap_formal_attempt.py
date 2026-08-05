"""Create and validate the first Formal attempt identity (after preflight PASS)."""
from __future__ import annotations

import argparse
import json
import socket
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from epoch_auth_r3.formal.identity import FormalAttemptIdV1


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--attempt-id", required=True)
    parser.add_argument("--attempt-root", required=True)
    parser.add_argument("--git-sha", required=True)
    parser.add_argument("--env-digest", required=True)
    parser.add_argument("--order-digest", required=True)
    parser.add_argument("--purpose", default="R3_FORMAL_MINIMUM_SUFFICIENT_E1_E5")
    args = parser.parse_args()
    if socket.gethostname() != "experiment-client":
        raise SystemExit("REMOTE_EXECUTION_REQUIRED")
    attempt = FormalAttemptIdV1.validate(args.attempt_id)
    root = Path(args.attempt_root)
    for child in ("raw", "runtime", "local-store", "state", "manifests"):
        (root / child).mkdir(parents=True, exist_ok=True)
    manifest = {
        "schemaVersion": "R3FormalAttemptManifestV1",
        "attemptId": attempt.serialize(),
        "attemptPurpose": args.purpose,
        "softwareCommit": args.git_sha,
        "environmentManifestDigest": args.env_digest,
        "executionOrderManifestDigest": args.order_digest,
        "remoteExecutionHost": "experiment-client",
        "remoteAttemptRoot": str(root),
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "state": "READY_FOR_WARMUP",
    }
    (root / "manifests/attempt-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (root / "state/attempt-state.json").write_text(
        json.dumps({"state": "READY_FOR_WARMUP"}, indent=2), encoding="utf-8"
    )
    print(json.dumps(manifest, sort_keys=True))


if __name__ == "__main__":
    main()
