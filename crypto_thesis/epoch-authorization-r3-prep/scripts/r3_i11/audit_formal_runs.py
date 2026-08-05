"""Remote audit: manifest ordinals vs sealed raw dirs vs block results."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--attempt-root", required=True)
    parser.add_argument("--runtime", required=True)
    args = parser.parse_args()
    manifest = json.loads(Path(args.manifest).read_text("utf-8"))
    raw = Path(args.attempt_root) / "raw"
    raw_ids = {p.name for p in raw.iterdir() if p.is_dir()}
    runtime = Path(args.runtime)
    block_files = sorted(runtime.glob("block-*.json"))
    block_lines = {}
    for block in block_files:
        block_lines[block.name] = sum(
            1 for line in block.read_text("utf-8").splitlines() if line.strip()
        )
    missing = []
    for entry in manifest["entries"]:
        if entry["runId"] not in raw_ids:
            missing.append({
                "ordinal": entry["ordinal"], "experiment": entry["experimentId"],
                "configIndex": entry["configIndex"], "repeat": entry["repeatIndex"],
                "warmup": entry["warmup"], "runId": entry["runId"],
            })
    extra = sorted(raw_ids - {e["runId"] for e in manifest["entries"]})
    print(json.dumps({
        "manifestRuns": len(manifest["entries"]),
        "rawDirs": len(raw_ids),
        "missing": missing,
        "missingCount": len(missing),
        "extraRawDirs": extra,
        "blockResultLines": block_lines,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
