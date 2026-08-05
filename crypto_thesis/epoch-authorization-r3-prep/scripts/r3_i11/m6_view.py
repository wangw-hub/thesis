# -*- coding: utf-8 -*-
"""M6: print M6 source chunks."""
from __future__ import annotations

import io
import sys
from pathlib import Path


ROOT = Path(r"D:\Research\crypto_thesis\epoch-authorization-r3-prep")
SRC = ROOT / "docs/midterm-report/m6/M6-MIDTERM-SOURCE.md"


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    t = io.open(SRC, encoding="utf-8").read()
    start = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    length = int(sys.argv[2]) if len(sys.argv) > 2 else 6000
    print(t[start:start + length])


if __name__ == "__main__":
    main()
