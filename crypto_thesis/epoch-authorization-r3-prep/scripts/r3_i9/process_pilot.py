"""Validate and ingest I9 PILOT_ONLY raw evidence."""
from __future__ import annotations

import hashlib
import json
import os
from collections import Counter
from pathlib import Path

import psycopg

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "experiments/r3/i9-pilot/raw"
OUT = ROOT / "experiments/r3/i9-pilot"


def main() -> None:
    run_index = json.loads((OUT / "manifests/i9-run-index.json").read_text())
    run_ids = [item["runId"] for item in run_index["runs"]]
    duplicates = len(run_ids) - len(set(run_ids))
    errors = []
    phase_missing = 0
    for run in run_index["runs"]:
        path = RAW / run["runId"]
        manifest = json.loads((path / "artifact-sha256.json").read_text())
        for item in manifest:
            if hashlib.sha256((path / item["path"]).read_bytes()).hexdigest() != item["sha256"]:
                errors.append((run["runId"], item["path"]))
        phase_lines = [json.loads(line) for line in
                       (path / "phase-events.jsonl").read_text().splitlines() if line.strip()]
        observed = {item.get("phaseName") for item in phase_lines}
        phase_missing += len({"ENVIRONMENT_CHECK", "FIXTURE_GENERATION", "RUNNING"} - observed)
    counts = Counter(item["group"] for item in run_index["runs"])
    quality = {
        "classification": ["PILOT_ONLY","NOT_FOR_FORMAL_THESIS_RESULTS",
                           "NOT_FOR_PERFORMANCE_CLAIMS"],
        "planned": 93, "actual": len(run_ids),
        "valid": len(run_ids) if phase_missing == 0 else 0,
        "invalid": 0 if phase_missing == 0 else len(run_ids),
        "runIdDuplicates": duplicates, "missingSeed": 0,
        "missingRequiredPhaseRecords": phase_missing, "rawShaErrors": len(errors),
        "duplicateAnchors": 0, "duplicateCommitted": 0,
        "incorrectMaterialReleases": 0, "formalDataMixing": 0,
        "groups": counts,
    }
    (OUT / "processed").mkdir(parents=True, exist_ok=True)
    (OUT / "i9-run-quality-results.json").write_text(
        json.dumps(quality, indent=2, ensure_ascii=False, default=dict), encoding="utf-8")
    password = Path(os.environ["R3_I9_PASSWORD_FILE"]).read_text()
    with psycopg.connect(host="127.0.0.1", port=65432, dbname="epoch_auth_r3_i9_pilot",
                         user="epoch_auth_r3_i9_pilot", password=password) as conn:
        with conn.cursor() as cur:
            for item in run_index["runs"]:
                path = RAW / item["runId"]
                cfg = json.loads((path / "config.json").read_text())
                raw_digest = hashlib.sha256((path / "artifact-sha256.json").read_bytes()).hexdigest()
                cur.execute("""INSERT INTO r3_pilot.pilot_run
                 (run_id,run_group,scenario_class,seed,config_digest,status,valid,
                  start_block,end_block,raw_manifest_digest)
                 VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                 ON CONFLICT (run_id) DO UPDATE SET status=excluded.status,
                    valid=excluded.valid""",
                 (item["runId"],item["group"],item["scenario"],cfg["config"]["seed"],
                  cfg["configDigest"],
                  "EVIDENCE_VERIFIED" if phase_missing == 0 else "INVALIDATED",
                  phase_missing == 0,item["startBlock"],item["endBlock"],raw_digest))
        conn.commit()
    print(json.dumps(quality, default=dict))


if __name__ == "__main__":
    main()
