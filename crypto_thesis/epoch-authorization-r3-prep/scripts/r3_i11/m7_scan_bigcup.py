# -*- coding: utf-8 -*-
"""M7: find every \\bigcup occurrence (display and inline) in the M7 source."""
from __future__ import annotations

import re
import sys


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    p = r"D:\Research\crypto_thesis\epoch-authorization-r3-prep\docs\midterm-report\m7\M7-MIDTERM-SOURCE.md"
    s = open(p, encoding="utf-8").read()
    for m in re.finditer(r"\\bigcup", s):
        start = max(0, m.start() - 60)
        print(repr(s[start: m.end() + 70]))


if __name__ == "__main__":
    main()
