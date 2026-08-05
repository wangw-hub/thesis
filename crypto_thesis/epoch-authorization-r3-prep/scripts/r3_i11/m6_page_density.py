# -*- coding: utf-8 -*-
"""M6: per-page density report."""
from __future__ import annotations

import sys
from pathlib import Path

import fitz


ROOT = Path(r"D:\Research\crypto_thesis\epoch-authorization-r3-prep")
PDF = ROOT / "docs/midterm-report/m6/output/王威-专业学位研究生学位论文中期考评表-M6候选稿.pdf"


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    doc = fitz.open(str(PDF))
    for i, p in enumerate(doc, 1):
        txt = p.get_text()
        lines = [ln.strip() for ln in txt.splitlines() if ln.strip()]
        first = lines[0][:70] if lines else "(blank)"
        print(f"p{i:02d} chars={len(txt):5d} lines={len(lines):3d} | {first}")


if __name__ == "__main__":
    main()
