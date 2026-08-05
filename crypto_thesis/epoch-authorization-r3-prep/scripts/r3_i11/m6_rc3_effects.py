# -*- coding: utf-8 -*-
"""M6: verify RC3 E2/E3/E4 text claims against frozen analysis."""
from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(r"D:\Research\crypto_thesis\epoch-authorization-r3-prep")


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    desc = json.loads((ROOT / "experiments/r3/formal/analysis/descriptive-statistics.json").read_text(encoding="utf-8"))
    effects = json.loads((ROOT / "experiments/r3/formal/analysis/effect-sizes.json").read_text(encoding="utf-8"))
    print("=== E2 medians ===")
    for k in sorted(desc):
        if k.startswith("E2"):
            print(k, round(desc[k]["median"], 1))
    print("=== E3 medians ===")
    for k in sorted(desc):
        if k.startswith("E3"):
            print(k, round(desc[k]["median"], 1))
    print("=== effect sizes ===")
    for k, v in effects.items():
        print(k, "|", json.dumps(v, ensure_ascii=False)[:260])


if __name__ == "__main__":
    main()
