# -*- coding: utf-8 -*-
"""M7: gather temporal evidence for experiment completion dates."""
from __future__ import annotations

import io
import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(r"D:\Research\crypto_thesis\epoch-authorization-r3-prep")


def git(cmd):
    r = subprocess.run(["git", "-C", str(ROOT)] + cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.stdout.strip()


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print("=== commits touching experiments/r3/formal ===")
    out = git(["log", "--format=%h %ad %s", "--date=iso", "--", "experiments/r3/formal"])
    print(out[:4000])
    print()
    print("=== commits touching i11/i12 ===")
    out = git(["log", "--format=%h %ad %s", "--date=iso", "--", "docs/research-content-3-implementation/i11", "docs/research-content-3-implementation/i12"])
    print(out[:3000])
    print()
    print("=== first/last commit dates overall ===")
    print("first:", git(["log", "--reverse", "--format=%h %ad", "--date=iso"]).splitlines()[0])
    print("last:", git(["log", "-1", "--format=%h %ad", "--date=iso"]))

    # evidence file timestamps
    for rel in [
        "experiments/r3/formal/analysis/descriptive-statistics.json",
        "experiments/r3/formal/analysis/bootstrap-results.json",
        "docs/research-content-3-implementation/i12/formal-rq-results.json",
        "docs/research-content-3-implementation/i11/formal-config-matrix.json",
    ]:
        p = ROOT / rel
        if p.exists():
            import os
            st = os.stat(p)
            import datetime
            print(rel, "mtime:", datetime.datetime.fromtimestamp(st.st_mtime).isoformat())


if __name__ == "__main__":
    main()
