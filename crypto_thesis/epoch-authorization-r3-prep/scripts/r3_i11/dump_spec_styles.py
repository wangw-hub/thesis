"""Dump key style definitions from the official writing-spec DOCX."""
from __future__ import annotations

import sys
from pathlib import Path

from docx import Document
from docx.oxml.ns import qn


SPEC = Path(r"D:\Users\wangw\Documents\xwechat_files\wxid_qxnxx2moo0vz22_5966\msg\file\2026-08\电子科技大学研究生学位论文撰写规范- 适用于中国学生 - 副本_031543351520.docx")

WANT = ["正文", "Heading 1", "Heading 2", "Heading 3", "Heading 4", "图题", "表题", "公式", "参考文献", "Normal", "List Paragraph"]


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    doc = Document(str(SPEC))
    for st in doc.styles:
        if st.name not in WANT and not st.name.startswith("Heading"):
            continue
        print("==== style:", st.name, "| type:", st.type)
        f = st.font
        print("  font size:", f.size.pt if f.size else None, "bold:", f.bold, "name:", f.name)
        rpr = st.element.find(qn("w:rPr"))
        if rpr is not None:
            rf = rpr.find(qn("w:rFonts"))
            if rf is not None:
                print("  rFonts ascii:", rf.get(qn("w:ascii")), "hAnsi:", rf.get(qn("w:hAnsi")),
                      "eastAsia:", rf.get(qn("w:eastAsia")))
        pf = st.paragraph_format
        print("  align:", pf.alignment, "| line:", pf.line_spacing, pf.line_spacing_rule,
              "| before:", pf.space_before.pt if pf.space_before else None,
              "| after:", pf.space_after.pt if pf.space_after else None,
              "| first_indent:", pf.first_line_indent.pt if pf.first_line_indent else None,
              "| keep_next:", pf.keep_with_next)

    # English school name for college 08
    for t in doc.tables:
        for row in t.rows:
            cells = [c.text.strip() for c in row.cells]
            if any("计算机科学与工程" in c for c in cells):
                print("COLLEGE ROW:", cells)


if __name__ == "__main__":
    main()
