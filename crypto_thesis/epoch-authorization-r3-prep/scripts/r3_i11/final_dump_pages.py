# -*- coding: utf-8 -*-
"""Dump raw PDF text for selected pages of the FINAL PDF."""
from __future__ import annotations

import sys

import pypdfium2 as pdfium


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    pdf = r"D:\Research\crypto_thesis\epoch-authorization-r3-prep\docs\midterm-report\final\output\王威-专业学位研究生学位论文中期考评表-最终固化版.pdf"
    doc = pdfium.PdfDocument(pdf)
    for p in [int(x) for x in sys.argv[1:]]:
        t = doc[p - 1].get_textpage().get_text_bounded()
        print("=" * 40, "PAGE", p, "=" * 40)
        print(t[:2800])


if __name__ == "__main__":
    main()
