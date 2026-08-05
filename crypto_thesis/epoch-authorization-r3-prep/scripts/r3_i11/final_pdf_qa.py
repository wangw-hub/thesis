# -*- coding: utf-8 -*-
"""FINAL: per-page PDF QA (text layer)."""
from __future__ import annotations

import json
import re
import sys

import pypdfium2 as pdfium


PDF = r"D:\Research\crypto_thesis\epoch-authorization-r3-prep\docs\midterm-report\final\output\王威-专业学位研究生学位论文中期考评表-最终固化版.pdf"


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    doc = pdfium.PdfDocument(PDF)
    pages = [doc[i].get_textpage().get_text_bounded() for i in range(len(doc))]
    report: dict = {}
    report["page_count"] = len(pages)

    p1 = pages[0]
    line = next((ln for ln in p1.splitlines() if "攻读学位级别" in ln), "")
    report["cover_degree_line_checked"] = line.count("☑")
    report["page2_blank_chars"] = len(pages[1].strip())

    suspects = []
    for i, t in enumerate(pages, 1):
        for ch in ("\ufffd", "□", "☐", "▢"):
            if ch in t and not (i == 1 or i == 3 or i == len(pages)):
                suspects.append({"page": i, "char": ch, "count": t.count(ch)})
    report["placeholder_chars"] = suspects

    # formula numbers (1)..(16) ascending
    found_eqs = {}
    for i, t in enumerate(pages, 1):
        for m in re.finditer(r"\((\d{1,2})\)", t):
            n = int(m.group(1))
            if 1 <= n <= 16:
                found_eqs.setdefault(n, []).append(i)
    firsts = [min(v) for _, v in sorted(found_eqs.items())]
    report["formula_first_pages"] = {n: min(v) for n, v in sorted(found_eqs.items())}
    report["formula_first_page_ascending"] = firsts == sorted(firsts)

    algo_pages = {}
    for i, t in enumerate(pages, 1):
        for m in re.finditer(r"算法\s*(\d+)", t):
            n = int(m.group(1))
            if 1 <= n <= 8 and n not in algo_pages:
                algo_pages[n] = i
    report["algo_pages"] = algo_pages
    report["all_algorithms_found"] = all(n in algo_pages for n in range(1, 9))
    report["algo6_before_algo7"] = algo_pages.get(6, 999) <= algo_pages.get(7, 999)

    fig_pages = {}
    for i, t in enumerate(pages, 1):
        for m in re.finditer(r"图\s*(\d{1,2})", t):
            n = int(m.group(1))
            if 1 <= n <= 20 and n not in fig_pages:
                fig_pages[n] = i
    report["missing_figures"] = [n for n in range(1, 21) if n not in fig_pages]

    tab_pages = {}
    for i, t in enumerate(pages, 1):
        for m in re.finditer(r"表\s*(\d{1,2})", t):
            n = int(m.group(1))
            if 1 <= n <= 8 and n not in tab_pages:
                tab_pages[n] = i
    report["missing_tables"] = [n for n in range(1, 9) if n not in tab_pages]
    report["table_pages"] = tab_pages

    anchors = ["阶段性研究成果", "存在的主要问题和解决办法", "中期考评审查意见"]
    report["anchors"] = {a: next((i + 1 for i, t in enumerate(pages) if a in t), None) for a in anchors}

    dense = []
    for i, t in enumerate(pages, 1):
        n = len(t.strip())
        if n < 30 and i != 2:
            dense.append({"page": i, "chars": n})
    report["low_density_pages"] = dense

    # access dates absent from reference text
    ref_text = "".join(pages[30:34])
    report["access_dates_visible"] = ref_text.count("[2026-08-02]") + ref_text.count("2014[")

    print(json.dumps(report, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
