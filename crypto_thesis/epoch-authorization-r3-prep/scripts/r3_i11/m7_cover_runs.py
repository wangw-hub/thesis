# -*- coding: utf-8 -*-
"""M7: dump raw run XML of cover paragraphs 2 and 3."""
from __future__ import annotations

import sys
from pathlib import Path

from docx import Document
from lxml import etree


ROOT = Path(r"D:\Research\crypto_thesis\epoch-authorization-r3-prep")
M6_DOCX = ROOT / "docs/midterm-report/m6/output/王威-专业学位研究生学位论文中期考评表-M6候选稿.docx"


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    doc = Document(str(M6_DOCX))
    for i, p in enumerate(doc.paragraphs[:14]):
        if "攻读学位级别" in p.text or "培养方式" in p.text:
            print("=" * 20, "paragraph", i, repr(p.text))
            xml = etree.tostring(p._p, encoding="unicode")
            # print run texts with codepoints
            for ri, r in enumerate(p.runs):
                cps = [f"U+{ord(c):04X}" for c in r.text if ord(c) > 0x2000 or ord(c) in (0x25A1, 0x2611)]
                print(f"  run{ri}: {r.text!r} special={cps}")
            # find w:sym elements
            for sym in p._p.iter("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}sym"):
                print("  w:sym font=", sym.get("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}font"),
                      "char=", sym.get("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}char"))


if __name__ == "__main__":
    main()
