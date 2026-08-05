# -*- coding: utf-8 -*-
"""M6: show double-space contexts."""
from __future__ import annotations

import io
import re
import sys
from pathlib import Path


ROOT = Path(r"D:\Research\crypto_thesis\epoch-authorization-r3-prep")
M6 = ROOT / "docs/midterm-report/m6/M6-MIDTERM-SOURCE.md"


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    t = io.open(M6, encoding="utf-8").read()
    for m in re.finditer(r" {2,}", t):
        ctx = t[max(0, m.start() - 45):m.end() + 45].replace("\n", " ")
        print(m.start(), "|", ctx)


if __name__ == "__main__":
    main()
