# -*- coding: utf-8 -*-
"""M6: check reference heading occurrences and list tail."""
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
        if "参考文献" in txt:
            for ln in txt.splitlines():
                if "参考文献" in ln:
                    print(f"p{i}: {ln.strip()[:70]}")
    print("=== last reference entries ===")
    tail = doc[31].get_text() + doc[32].get_text()
    for ln in tail.splitlines():
        if ln.strip().startswith("[3") or ln.strip().startswith("[31"):
            print(ln.strip()[:110])


if __name__ == "__main__":
    main()
