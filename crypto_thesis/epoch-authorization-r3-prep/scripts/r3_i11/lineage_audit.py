"""Read-only Formal attempt lineage audit on experiment-client."""
from __future__ import annotations

import json
from pathlib import Path


def main() -> None:
    attempts = sorted(Path("/var/lib/epoch-auth-r3/formal/attempts").glob("FORMAL_*"))
    records = []
    for attempt_dir in attempts:
        raw_count = sum(1 for _ in (attempt_dir / "raw").iterdir()) if (attempt_dir / "raw").is_dir() else 0
        manifest_path = attempt_dir / "manifests" / "attempt-manifest.json"
        manifest = None
        if manifest_path.exists():
            manifest = json.loads(manifest_path.read_text("utf-8"))
        freeze = None
        for note in ("state/freeze-note.txt", "state/freeze-note.json"):
            p = attempt_dir / note
            if p.exists():
                freeze = p.read_text("utf-8").strip()
        records.append({
            "attemptId": attempt_dir.name,
            "softwareCommit": manifest.get("softwareCommit") if manifest else None,
            "orderDigest": manifest.get("executionOrderManifestDigest") if manifest else None,
            "rawDirCount": raw_count,
            "state": manifest.get("state") if manifest else None,
            "freezeNote": freeze,
        })
    print(json.dumps(records, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
