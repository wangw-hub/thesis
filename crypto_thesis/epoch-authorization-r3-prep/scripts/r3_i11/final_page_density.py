# -*- coding: utf-8 -*-
"""Per-page text density for the FINAL PDF."""
from __future__ import annotations

import sys

import pypdfium2 as pdfium


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    pdf = r"D:\Research\crypto_thesis\epoch-authorization-r3-prep\docs\midterm-report\final\output\王威-专业学位研究生学位论文中期考评表-最终固化版.pdf"
    doc = pdfium.PdfDocument(pdf)
    for i in range(len(doc)):
        t = doc[i].get_textpage().get_text_bounded()
        n = len(t.strip())
        first = " ".join(t.strip().splitlines()[:1])[:40]
        print(f"page {i+1:02d}: chars={n:5d} | {first}")


if __name__ == "__main__":
    main()
