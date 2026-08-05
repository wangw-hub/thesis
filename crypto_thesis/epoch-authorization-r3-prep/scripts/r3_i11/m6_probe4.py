# -*- coding: utf-8 -*-
"""M6: probe the transformed M6 source for leftovers."""
from __future__ import annotations

import io
import re
import sys
from pathlib import Path


ROOT = Path(r"D:\Research\crypto_thesis\epoch-authorization-r3-prep")
SRC = ROOT / "docs/midterm-report/m6/M6-MIDTERM-SOURCE.md"


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    t = io.open(SRC, encoding="utf-8").read()
    print("=== remaining equation markers ===")
    for m in re.finditer(r"\[公式：([^\]]+)\]", t):
        print(m.start(), "|", m.group(1)[:120])
    print()
    print("=== remaining forbidden tags ===")
    for tag in ["E2", "E3", "E5", "E1", "RC2", "RC3", "CAP2", "V13", "Pilot", "RUN", "LOCAL_ONLY", "KUBO_REPLICA"]:
        for m in re.finditer(re.escape(tag), t):
            ctx = t[max(0, m.start() - 50):m.end() + 50].replace("\n", " ")
            print(tag, "@", m.start(), "|", ctx)
    print()
    print("=== figure markers ===")
    for m in re.finditer(r"\[方法图：([^\]]+)\]", t):
        print(m.group(1))
    print()
    print("=== I* formula check ===")
    for m in re.finditer(r"I\^\*", t):
        ctx = t[max(0, m.start() - 40):m.end() + 40].replace("\n", " ")
        print(m.start(), "|", ctx)


if __name__ == "__main__":
    main()
