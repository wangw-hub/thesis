# -*- coding: utf-8 -*-
"""M6: locate recovery-duration numbers in frozen results."""
from __future__ import annotations

import io
import sys
from pathlib import Path


ROOT = Path(r"D:\Research\crypto_thesis\epoch-authorization-r3-prep")


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    targets = [
        ROOT / "docs/research-content-3-implementation/i12/11-RQ5-RQ6-RESULT.md",
        ROOT / "docs/research-content-3-implementation/i12/formal-rq-results.json",
        ROOT / "docs/research-content-3-implementation/i12/thesis-ready-result-dataset.json",
        ROOT / "experiments/r3/formal/analysis/descriptive-statistics.json",
        ROOT / "experiments/r3/formal/analysis/bootstrap-results.json",
    ]
    for p in targets:
        if not p.exists():
            print("missing", p)
            continue
        t = p.read_text(encoding="utf-8", errors="replace")
        print("=" * 20, p.name)
        for ln in t.splitlines():
            if "3112" in ln or "3129" in ln or "recovery" in ln.lower() or "恢复" in ln:
                if len(ln) < 300:
                    print(ln[:260])


if __name__ == "__main__":
    main()
