# -*- coding: utf-8 -*-
"""M6: show equation page text from PDF."""
from __future__ import annotations

import sys
from pathlib import Path

import fitz


ROOT = Path(r"D:\Research\crypto_thesis\epoch-authorization-r3-prep")
PDF = ROOT / "docs/midterm-report/m6/output/王威-专业学位研究生学位论文中期考评表-M6候选稿.pdf"


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    doc = fitz.open(str(PDF))
    page_no = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    txt = doc[page_no - 1].get_text()
    lines = [ln for ln in txt.splitlines() if ln.strip()]
    for i, ln in enumerate(lines):
        if "(" in ln and any(ch.isdigit() for ch in ln):
            print(f"{i:02d}| {ln[:110]}")


if __name__ == "__main__":
    main()
