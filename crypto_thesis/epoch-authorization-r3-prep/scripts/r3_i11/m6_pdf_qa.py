# -*- coding: utf-8 -*-
"""M6: programmatic PDF QA (text, tags, equations, algorithms, images)."""
from __future__ import annotations

import io
import json
import re
import sys
from pathlib import Path

import fitz


ROOT = Path(r"D:\Research\crypto_thesis\epoch-authorization-r3-prep")
PDF = ROOT / "docs/midterm-report/m6/output/王威-专业学位研究生学位论文中期考评表-M6候选稿.pdf"


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    doc = fitz.open(str(PDF))
    pages = [doc[i] for i in range(len(doc))]
    all_text = "\n".join(p.get_text() for p in pages)

    report = {"pages": len(pages)}

    # blank pages
    blank = [i + 1 for i, p in enumerate(pages) if len(p.get_text().strip()) < 20]
    report["blank_pages"] = blank

    # forbidden tags
    tags = ["RC1", "RC2", "RC3", "E1-A", "E1-B", "E1-C", "E2", "E3", "E4", "E5",
            "V13", "v13", "P9", "Pilot", "Formal", "attempt", "runId",
            "CAP2", "Baseline-I", "Proposed-C", "HEADER_ONLY", "BODY_ROTATION",
            "LOCAL_ONLY", "KUBO_REPLICA", "INITIAL", "REVOCATION", "RESTORE"]
    tag_hits = {}
    for tag in tags:
        n = all_text.count(tag)
        if n:
            tag_hits[tag] = n
    report["forbidden_tag_hits"] = tag_hits

    # equation numbers
    eq_nums = re.findall(r"\((\d{1,2})\)", all_text)
    report["eq_number_occurrences"] = [int(x) for x in eq_nums if int(x) <= 20]

    # algorithm titles
    algos = [f"算法{i}" for i in range(1, 9)]
    report["algorithm_titles"] = {a: all_text.count(a) for a in algos}
    report["algo_end_text"] = all_text.count("算法结束")

    # reference headings
    report["reference_heading_count"] = len(re.findall(r"参考文献", all_text))
    ref_entries = re.findall(r"^\[\d{1,2}\] ", all_text, re.M)
    report["reference_entries_in_pdf"] = len(ref_entries)

    # placeholder / garbage
    for pat in ["□", "\ufffd", "MISSING", "placeholder", "�"]:
        n = all_text.count(pat)
        if n:
            report.setdefault("placeholder_hits", {})[pat] = n

    # figure captions count
    caps = re.findall(r"图\d+ [^\n]+", all_text)
    report["figure_caption_like"] = len(caps)
    table_caps = re.findall(r"表\d+ [^\n]+", all_text)
    report["table_caption_like"] = len(table_caps)

    # images per page (size in points)
    img_report = []
    for i, p in enumerate(pages, 1):
        for img in p.get_images(full=True):
            try:
                rect = p.get_image_rects(img[0])
                if rect:
                    r = rect[0]
                    img_report.append({"page": i, "w_pt": round(r.width, 1), "h_pt": round(r.height, 1)})
            except Exception:
                pass
    report["image_count"] = len(img_report)
    report["image_max_width_pt"] = max((x["w_pt"] for x in img_report), default=0)
    report["images_gt_420pt"] = [x for x in img_report if x["w_pt"] > 420]

    # per-page first line (for layout spot check)
    report["page_first_lines"] = [pages[i].get_text().strip().splitlines()[0][:60] if pages[i].get_text().strip() else "(blank)" for i in range(len(pages))]

    out = ROOT / "docs/midterm-report/m6/qa-pages/_pdf_qa.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({
        "pages": report["pages"],
        "blank_pages": report["blank_pages"],
        "forbidden_tag_hits": report["forbidden_tag_hits"],
        "algo_end_text": report["algo_end_text"],
        "reference_heading_count": report["reference_heading_count"],
        "reference_entries_in_pdf": report["reference_entries_in_pdf"],
        "figure_caption_like": report["figure_caption_like"],
        "table_caption_like": report["table_caption_like"],
        "image_count": report["image_count"],
        "images_gt_420pt": len(report["images_gt_420pt"]),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
