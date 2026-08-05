# -*- coding: utf-8 -*-
"""M7: scan for duplicated labels / double spaces / stray artifacts."""
from __future__ import annotations

import re
import sys


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    p = r"D:\Research\crypto_thesis\epoch-authorization-r3-prep\docs\midterm-report\m7\M7-MIDTERM-SOURCE.md"
    s = open(p, encoding="utf-8").read()
    print("--- duplicated word-ish labels ---")
    for m in re.finditer(r"([\u4e00-\u9fa5A-Za-z]{2,8})\s+\1", s):
        print(repr(s[max(0, m.start() - 30): m.end() + 30]))
    print("--- double spaces inside CJK lines ---")
    for i, ln in enumerate(s.split("\n"), 1):
        if re.search(r"[\u4e00-\u9fa5] {2,}[\u4e00-\u9fa5]", ln):
            print(i, repr(ln[:120]))
    print("--- stray '  ' before specific terms ---")
    for pat in ("期间 验证方", "撤销后的 未闭合", "隔离副本 从", "实验 覆盖"):
        hits = [m.start() for m in re.finditer(re.escape(pat), s)]
        if hits:
            for h in hits:
                print(pat, "=>", repr(s[h - 25: h + 40]))


if __name__ == "__main__":
    main()
