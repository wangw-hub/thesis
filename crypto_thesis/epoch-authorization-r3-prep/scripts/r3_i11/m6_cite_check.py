# -*- coding: utf-8 -*-
"""M6: verify first-citation order and equation anchor consistency."""
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
    body = t[: t.find("### 参考文献")]

    # tokenize citation anchors: [1], [1-3], [1,4], [1][2]
    anchors = re.findall(r"\[(\d+)(?:-(\d+))?(?:,(\d+))?\]", body)
    first_seen = []
    for a in anchors:
        lo = int(a[0])
        hi = int(a[1]) if a[1] else lo
        for n in range(lo, hi + 1):
            if n not in first_seen:
                first_seen.append(n)
    print("first-seen order:", first_seen)
    expected = list(range(1, len(first_seen) + 1))
    print("in-order:", first_seen == expected)
    missing = [n for n in range(1, 32) if n not in first_seen]
    print("refs never cited in body:", missing)

    # equation number references
    eqrefs = re.findall(r"式（(\d+)）", body)
    print("equation refs in text:", eqrefs)
    # expected display equation order
    markers = [m.group(1)[:60] for m in re.finditer(r"\[公式：([^\]]+)\]", t)]
    print("display equations in order (%d):" % len(markers))
    for i, m in enumerate(markers, 1):
        print(i, "|", m)


if __name__ == "__main__":
    main()
