# -*- coding: utf-8 -*-
"""M7: map PDF pages to key content markers for visual QA targeting."""
from __future__ import annotations

import sys

import pypdfium2 as pdfium


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    pdf = r"D:\Research\crypto_thesis\epoch-authorization-r3-prep\docs\midterm-report\m7\output\王威-专业学位研究生学位论文中期考评表-M7最终候选稿.pdf"
    doc = pdfium.PdfDocument(pdf)
    markers = [
        "攻读学位级别", "研究内容一", "研究内容二", "研究内容三",
        "算法1", "算法2", "算法3", "算法4", "算法5", "算法6", "算法7", "算法8",
        "表1", "表2", "表3", "表4", "表5", "表6", "表7", "表8",
        "图1", "图5", "图10", "图15", "图16", "图20",
        "参考文献", "阶段性研究成果", "存在的主要问题", "中期考评审查意见",
        "（1）", "（10）", "（13）", "（14）", "（15）", "（16）",
    ]
    for i in range(len(doc)):
        text = doc[i].get_textpage().get_text_bounded()
        hits = [m for m in markers if m in text]
        if hits:
            print(f"page {i + 1:02d}: {hits}")


if __name__ == "__main__":
    main()
