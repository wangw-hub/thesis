# -*- coding: utf-8 -*-
"""M7: dump page 1 and 2 text from M6 PDF."""
from __future__ import annotations

import sys
from pathlib import Path

import fitz


ROOT = Path(r"D:\Research\crypto_thesis\epoch-authorization-r3-prep")
PDF = ROOT / "docs/midterm-report/m6/output/王威-专业学位研究生学位论文中期考评表-M6候选稿.pdf"


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    doc = fitz.open(str(PDF))
    print("=== page 1 ===")
    print(doc[0].get_text())
    print("=== page 2 ===")
    t2 = doc[1].get_text()
    print("chars:", len(t2.strip()), repr(t2[:120]))


if __name__ == "__main__":
    main()
