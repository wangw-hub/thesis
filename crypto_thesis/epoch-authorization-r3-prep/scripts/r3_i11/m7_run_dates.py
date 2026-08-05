# -*- coding: utf-8 -*-
"""M7: find actual RC3 experiment run dates from evidence/manifests."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(r"D:\Research\crypto_thesis\epoch-authorization-r3-prep")


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    probes = [
        ROOT / "experiments/r3/formal/manifests/formal-execution-order.json",
        ROOT / "experiments/r3/formal/manifests/formal-fingerprint.json",
        ROOT / "experiments/r3/formal/manifests/attempt-manifest.json",
        ROOT / "experiments/r3/formal/manifests/formal-preflight.json",
        ROOT / "experiments/r3/formal/analysis/accepted-run-index.json",
        ROOT / "experiments/r3/formal/analysis/analysis-manifest.json",
    ]
    for p in probes:
        if not p.exists():
            print("missing", p.relative_to(ROOT))
            continue
        print("=" * 20, p.relative_to(ROOT))
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except Exception as exc:
            print("parse error:", exc)
            continue
        s = json.dumps(d, ensure_ascii=False)
        dates = sorted(set(re.findall(r"20\d{2}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}", s)))
        print("datetimes found:", dates[:20])
        for key in ["generatedAt", "executionStartedAt", "executionEndedAt", "startedAt", "endedAt", "createdAt", "timestamp"]:
            if isinstance(d, dict) and d.get(key):
                print(key, "=", d[key])

    # raw run dirs: check a few run-state/config timestamps
    raw = ROOT / "experiments/r3/formal/raw"
    subdirs = sorted(raw.iterdir())[:3]
    for d in subdirs:
        for fname in ["run-state.json", "config.json", "phase-contract.json"]:
            p = d / fname
            if p.exists():
                t = p.read_text(encoding="utf-8", errors="replace")
                dates = sorted(set(re.findall(r"20\d{2}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}", t)))
                if dates:
                    print(p.relative_to(ROOT), "->", dates[:6])


if __name__ == "__main__":
    main()
