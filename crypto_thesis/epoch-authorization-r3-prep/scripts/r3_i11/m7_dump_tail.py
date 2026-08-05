# -*- coding: utf-8 -*-
"""M7: dump tail of a PDF page."""
from __future__ import annotations

import sys

import pypdfium2 as pdfium


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    pdf = r"D:\Research\crypto_thesis\epoch-authorization-r3-prep\docs\midterm-report\m7\output\王威-专业学位研究生学位论文中期考评表-M7最终候选稿.pdf"
    doc = pdfium.PdfDocument(pdf)
    p = int(sys.argv[1])
    t = doc[p - 1].get_textpage().get_text_bounded()
    print(t[-1500:])


if __name__ == "__main__":
    main()
