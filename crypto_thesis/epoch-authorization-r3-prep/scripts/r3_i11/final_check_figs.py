# -*- coding: utf-8 -*-
"""Check every 方法图 marker resolves in the FINAL build FIGURE_MAP."""
from __future__ import annotations

import re
import sys


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    src = open(
        r"D:\Research\crypto_thesis\epoch-authorization-r3-prep\docs\midterm-report\final\FINAL-MIDTERM-SOURCE.md",
        encoding="utf-8",
    ).read()
    build = open(
        r"D:\Research\crypto_thesis\epoch-authorization-r3-prep\scripts\r3_i11\build_final_docx.py",
        encoding="utf-8",
    ).read()
    caps = re.findall(r'\(\s*"(图\d+ [^"]+)"\s*,\s*SYSTEM_FIG|EXP_FIG', build)
    # parse FIGURE_MAP entries: ("图N ...", PATH, width)
    entries = re.findall(r'\("(图\d+ [^"]+)",\s*(SYSTEM_FIG|EXP_FIG)\s*/\s*"[^"]+"', build)
    for m in re.finditer(r"\[方法图：(图\d+[^\]]*)\]", src):
        marker = m.group(1)
        ok = any(cap in marker for cap, _ in entries)
        if not ok:
            print("UNRESOLVED:", marker)
    print("map entries:", len(entries))
    for cap, srcname in entries:
        print(" ", srcname, "|", cap)


if __name__ == "__main__":
    main()
