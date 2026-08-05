"""Audit the M3 midterm PDF: page count, key content, section spread."""
from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(r"D:\Research\crypto_thesis\epoch-authorization-r3-prep")
PDF = ROOT / "docs/midterm-report/m3/output/王威-专业学位研究生学位论文中期考评表-M3候选稿.pdf"


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    import pypdfium2 as pdfium

    doc = pdfium.PdfDocument(str(PDF))
    print("pages:", len(doc))
    pages = [doc[i].get_textpage().get_text_range() for i in range(len(doc))]
    full = "\n".join(pages)
    for kw in ["15120", "98.61", "9720", "233280", "145", "FAIL_CLOSED",
               "202422081113", "王威", "高建彬", "计算机技术", "参考文献",
               "（1）论文的理论抽象", "（3）实验规模与外部有效性", "下一步具体研究计划"]:
        print(f"{kw}: {full.count(kw)}")
    for i, p in enumerate(pages):
        if "存在的主要问题和解决办法" in p:
            print("problems section starts on page", i + 1)
        if "参考文献" in p and "Bertino" in p:
            print("references start on page", i + 1)
        if "阶段性研究成果" in p:
            print("stage results on page", i + 1)
    print("page1 head:", pages[0][:80].replace("\n", " "))


if __name__ == "__main__":
    main()
