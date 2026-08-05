# -*- coding: utf-8 -*-
"""M7: dump raw PDF text for selected pages."""
from __future__ import annotations

import sys

import pypdfium2 as pdfium


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    pdf = r"D:\Research\crypto_thesis\epoch-authorization-r3-prep\docs\midterm-report\m7\output\王威-专业学位研究生学位论文中期考评表-M7最终候选稿.pdf"
    doc = pdfium.PdfDocument(pdf)
    for p in [int(x) for x in sys.argv[1:]]:
        t = doc[p - 1].get_textpage().get_text_bounded()
        print("=" * 40, "PAGE", p, "=" * 40)
        print(t[:2600])


if __name__ == "__main__":
    main()
