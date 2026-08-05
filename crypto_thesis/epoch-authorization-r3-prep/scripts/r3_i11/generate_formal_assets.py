"""Generate I11 frozen execution assets (config matrix, order manifest, plan).

Deterministic: block key = semantic_class/experimentId/configuration_digest,
seed = 20260802.  Design-only; never contacts the Formal environment.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from epoch_auth_r3.formal.matrix import build_execution_order, measured_matrix, warmup_matrix


OUT = ROOT / "docs" / "research-content-3-implementation" / "i11"


def git_head() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    head = git_head()
    created = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    OUT.mkdir(parents=True, exist_ok=True)
    measured = measured_matrix()
    warmups = warmup_matrix()
    config_summary = {}
    for row in measured:
        key = row.experimentId
        config_summary.setdefault(key, []).append(row.to_dict())
    env_digest = "PENDING_ENVIRONMENT_FINGERPRINT"
    attempt_id = "FORMAL_PENDING"
    manifest = build_execution_order(
        attempt_id=attempt_id, software_commit=head, env_digest=env_digest,
    )
    matrix_digest = sha256_bytes(
        json.dumps({
            "measured": [r.to_dict() for r in measured],
            "warmups": [r.to_dict() for r in warmups],
        }, sort_keys=True, separators=(",", ":")).encode("utf-8")
    )
    (OUT / "formal-config-matrix.json").write_text(
        json.dumps({
            "schemaVersion": "R3FormalConfigMatrixV1",
            "measuredConfigs": len(measured),
            "warmupConfigs": len(warmups),
            "matrixDigest": matrix_digest,
            "measured": [r.to_dict() for r in measured],
            "warmups": [r.to_dict() for r in warmups],
        }, ensure_ascii=False, indent=2), encoding="utf-8",
    )
    (OUT / "formal-execution-order.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8",
    )
    print(json.dumps({
        "gitCommit": head, "createdAt": created,
        "measuredConfigs": len(measured), "warmupConfigs": len(warmups),
        "orderDigest": manifest["executionOrderManifestDigest"],
        "matrixDigest": matrix_digest,
        "output": str(OUT),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
