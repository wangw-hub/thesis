"""Populate r3_formal.formal_run from sealed remote raw evidence (read-only)."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from epoch_auth_r3.formal.database import (
    FormalDatabaseConnectionFactoryV1, frozen_formal_database_config,
    FormalApplicationNameV1, FormalDatabaseConnectionRoleV1,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--attempt-root", required=True)
    parser.add_argument("--db-password", required=True)
    parser.add_argument("--commit", required=True)
    args = parser.parse_args()
    root = Path(args.attempt_root)
    app_name = FormalApplicationNameV1.generate(
        attempt_id="FORMAL_INDEX", run_identity="0" * 64,
        role=FormalDatabaseConnectionRoleV1.EVIDENCE, software_commit=args.commit,
    )
    factory = FormalDatabaseConnectionFactoryV1(
        frozen_formal_database_config(app_name.value), Path(args.db_password)
    )
    indexed = 0
    with factory.connect() as conn:
        for run_dir in sorted((root / "raw").iterdir()):
            if not run_dir.is_dir():
                continue
            manifest = json.loads(
                (run_dir / "artifact-sha256.json").read_text("utf-8")
            )
            raw_digest = hashlib.sha256(
                json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode("utf-8")
            ).hexdigest()
            config = json.loads((run_dir / "config.json").read_text("utf-8"))
            run_state = json.loads((run_dir / "run-state.json").read_text("utf-8"))
            chain = json.loads((run_dir / "chain-evidence.json").read_text("utf-8"))
            cfg = config["config"]
            with conn.cursor() as cur:
                cur.execute("""INSERT INTO r3_formal.formal_run
                    (run_id, attempt_id, experiment_id, scenario_class, semantic_class,
                     config_digest, repeat_index, warmup, status, valid, disposition,
                     start_block, end_block, raw_manifest_digest, classification)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'FORMAL_EXPERIMENT')
                    ON CONFLICT (run_id) DO NOTHING""",
                    (
                        config["runId"], config["attemptId"], cfg["experimentId"],
                        cfg["scenarioClass"], cfg["semanticClass"],
                        config["configDigest"], cfg["repeatIndex"], cfg["warmup"],
                        run_state.get("status", "SEALED"), bool(run_state.get("valid")),
                        run_state.get("disposition", "UNKNOWN"),
                        chain.get("startBlock"), chain.get("endBlock"), raw_digest,
                    ))
                indexed += cur.rowcount
            conn.commit()
    print(json.dumps({"schemaVersion": "R3FormalRunIndexV1", "indexed": indexed,
                      "attemptRoot": str(root)}, sort_keys=True))


if __name__ == "__main__":
    main()
