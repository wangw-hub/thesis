"""Audit the M2 midterm PDF: page count, key content, figures/tables."""
from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(r"D:\Research\crypto_thesis\epoch-authorization-r3-prep")
PDF = ROOT / "docs/midterm-report/m2/output/王威-专业学位研究生学位论文中期考评表-M2候选稿.pdf"


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    import pypdfium2 as pdfium

    doc = pdfium.PdfDocument(str(PDF))
    print("pages:", len(doc))
    full = "\n".join(doc[i].get_textpage().get_text_range() for i in range(len(doc)))
    for kw in ["15120", "98.61", "81 项", "9720", "196", "98.66", "145", "FAIL_CLOSED",
               "202422081113", "王威", "高建彬", "计算机技术", "拟投稿", "图 1", "图 8",
               "开题报告通过时间"]:
        print(f"{kw}: {full.count(kw)}")
    # find where 存在问题 section starts
    i = full.find("存在的主要问题和解决办法")
    print("problems section page estimate:", i)
    # count pages roughly by checking page 20 content
    p20 = doc[19].get_textpage().get_text_range()
    print("page20 head:", p20[:60].replace("\n", " "))


if __name__ == "__main__":
    main()
