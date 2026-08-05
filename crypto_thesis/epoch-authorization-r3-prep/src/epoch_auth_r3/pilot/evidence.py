from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path


REQUIRED = {
    "config.json", "environment.json", "run-state.json", "phase-events.jsonl",
    "chain-evidence.json", "database-evidence.json", "object-evidence.json",
    "ipfs-evidence.json", "fault-evidence.json", "stdout.log", "stderr.log",
}
V2_FILES = {
    "failure-context.json", "phase-contract.json", "chain-write-plan.json",
    "database-transaction-evidence.json", "chain-transaction-evidence.json",
    "material-release-evidence.json", "evidence-accumulator.jsonl",
    "payload-artifact-sha256.json", "final-run-envelope-sha256.json",
}


class PilotEvidenceWriter:
    def __init__(self, raw_root: Path, run_id: str):
        if not raw_root.name == "raw" or len(run_id) != 64:
            raise ValueError("INVALID_PILOT_EVIDENCE_PATH")
        self.root = raw_root / run_id
        self.root.mkdir(parents=True, exist_ok=False)

    def write_once(self, name: str, value: dict | str) -> None:
        if name not in REQUIRED | V2_FILES or (self.root / name).exists():
            raise ValueError("RAW_EVIDENCE_IMMUTABLE")
        payload = value if isinstance(value, str) else json.dumps(
            value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        )
        (self.root / name).write_text(payload, encoding="utf-8", newline="\n")

    def seal(self) -> dict:
        missing = REQUIRED - {p.name for p in self.root.iterdir()}
        if missing:
            raise ValueError("MISSING_RAW_EVIDENCE")
        payload_items = []
        for path in sorted(self.root.iterdir()):
            if path.name in {
                "artifact-sha256.json", "payload-artifact-sha256.json",
                "final-run-envelope-sha256.json",
            }:
                continue
            payload_items.append({"path": path.name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
        payload = self.root / "payload-artifact-sha256.json"
        payload.write_text(json.dumps(payload_items, sort_keys=True, separators=(",", ":")),
                           encoding="utf-8", newline="\n")
        envelope_items = [{
            "path": payload.name, "sha256": hashlib.sha256(payload.read_bytes()).hexdigest()
        }]
        envelope = self.root / "final-run-envelope-sha256.json"
        envelope.write_text(json.dumps(envelope_items, sort_keys=True, separators=(",", ":")),
                            encoding="utf-8", newline="\n")
        items = payload_items + envelope_items + [{
            "path": envelope.name, "sha256": hashlib.sha256(envelope.read_bytes()).hexdigest()
        }]
        target = self.root / "artifact-sha256.json"
        target.write_text(json.dumps(items, sort_keys=True, separators=(",", ":")),
                          encoding="utf-8", newline="\n")
        for path in self.root.iterdir():
            os.chmod(path, 0o444)
        os.chmod(self.root, 0o555)
        return {"files": len(items), "errors": 0}


def validate_raw_run(path: Path) -> list[str]:
    errors = []
    if not REQUIRED <= {p.name for p in path.iterdir()}:
        errors.append("MISSING_RAW_EVIDENCE")
    manifest = json.loads((path / "artifact-sha256.json").read_text(encoding="utf-8"))
    for item in manifest:
        if hashlib.sha256((path / item["path"]).read_bytes()).hexdigest() != item["sha256"]:
            errors.append("RAW_SHA_MISMATCH")
    return errors
