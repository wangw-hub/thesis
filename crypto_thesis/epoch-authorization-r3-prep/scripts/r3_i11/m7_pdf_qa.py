# -*- coding: utf-8 -*-
"""M7: programmatic per-page PDF QA (text layer)."""
from __future__ import annotations

import json
import re
import sys

import pypdfium2 as pdfium


PDF = r"D:\Research\crypto_thesis\epoch-authorization-r3-prep\docs\midterm-report\m7\output\王威-专业学位研究生学位论文中期考评表-M7最终候选稿.pdf"


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    doc = pdfium.PdfDocument(PDF)
    pages = []
    for i in range(len(doc)):
        pages.append(doc[i].get_textpage().get_text_bounded())

    report: dict = {}
    report["page_count"] = len(pages)

    # page 1 cover: exactly one check mark on degree line
    p1 = pages[0]
    line = next((ln for ln in p1.splitlines() if "攻读学位级别" in ln), "")
    report["cover_degree_line_checked"] = line.count("☑")
    report["cover_degree_line_checkedbox"] = line.count("☒") + line.count("✔")

    # official blank page 2
    p2 = pages[1].strip()
    report["page2_blank_chars"] = len(p2)

    # suspicious placeholder characters anywhere
    suspects = []
    for i, t in enumerate(pages, 1):
        for ch in ("\ufffd", "□", "☐", "▢", "?"):
            if ch in t:
                suspects.append({"page": i, "char": ch, "count": t.count(ch)})
    report["placeholder_chars"] = suspects

    # formula numbers (1)..(16) in ascending page order
    eq_pages = {}
    for i, t in enumerate(pages, 1):
        for m in re.finditer(r"\((\d+)\)\s*$", t, re.M):
            pass
        for m in re.finditer(r"^\s*\((\d+)\)\s*$", t, re.M):
            eq_pages.setdefault(int(m.group(1)), []).append(i)
        # equations sit at line end after a tab; also match mid-line end
        for m in re.finditer(r"\((\d+)\)(\s|$)", t):
            pass
    # fallback: formula numbers are at the right side; extract "(n)" tokens
    found_eqs = {}
    for i, t in enumerate(pages, 1):
        for m in re.finditer(r"\((\d{1,2})\)", t):
            n = int(m.group(1))
            if 1 <= n <= 16:
                found_eqs.setdefault(n, []).append(i)
    order = []
    for n in range(1, 17):
        if n in found_eqs:
            order.append((n, min(found_eqs[n])))
    report["formula_numbers_found"] = {n: pages for n, pages in found_eqs.items()}
    first_pages = [p for _, p in order]
    report["formula_first_page_ascending"] = first_pages == sorted(first_pages)

    # algorithms in page order
    algo_pages = {}
    for i, t in enumerate(pages, 1):
        for m in re.finditer(r"算法\s*(\d+)", t):
            n = int(m.group(1))
            if 1 <= n <= 8 and n not in algo_pages:
                algo_pages[n] = i
    report["algo_pages"] = algo_pages
    p6 = algo_pages.get(6, 999)
    p7 = algo_pages.get(7, 999)
    report["algo6_page"] = p6
    report["algo7_page"] = p7
    report["algo6_before_algo7"] = p6 < p7
    report["all_algorithms_found"] = all(n in algo_pages for n in range(1, 9))

    # figure captions 图1..图20 and table captions 表1..表8
    fig_pages = {}
    for i, t in enumerate(pages, 1):
        for m in re.finditer(r"图\s*(\d{1,2})", t):
            n = int(m.group(1))
            if 1 <= n <= 20 and n not in fig_pages:
                fig_pages[n] = i
    report["figures_found"] = sorted(fig_pages.keys())
    report["missing_figures"] = [n for n in range(1, 21) if n not in fig_pages]

    tab_pages = {}
    for i, t in enumerate(pages, 1):
        for m in re.finditer(r"表\s*(\d{1,2})", t):
            n = int(m.group(1))
            if 1 <= n <= 8 and n not in tab_pages:
                tab_pages[n] = i
    report["tables_found"] = sorted(tab_pages.keys())
    report["missing_tables"] = [n for n in range(1, 9) if n not in tab_pages]
    report["table_pages"] = tab_pages

    # section anchors
    anchors = ["阶段性研究成果", "存在的主要问题和解决办法", "中期考评审查意见"]
    report["anchors"] = {a: next((i + 1 for i, t in enumerate(pages) if a in t), None) for a in anchors}

    # per-page density: flag suspiciously empty pages (except official page 2)
    dense = []
    for i, t in enumerate(pages, 1):
        n = len(t.strip())
        if n < 30 and i != 2:
            dense.append({"page": i, "chars": n})
    report["low_density_pages"] = dense

    print(json.dumps(report, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
