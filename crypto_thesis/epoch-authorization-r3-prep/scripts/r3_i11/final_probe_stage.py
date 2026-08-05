# -*- coding: utf-8 -*-
"""Probe stage-paper / patent files for the stage-result truth audit."""
from __future__ import annotations

import sys

from docx import Document


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    files = [
        r"D:\Users\wangw\Desktop\中期和小论文\学位论文小论文.docx",
        r"D:\Users\wangw\Desktop\中期和小论文\一种基于数据网格的陷门双重绑定可信数据共享方案v1.0.docx",
    ]
    for f in files:
        try:
            doc = Document(f)
            paras = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
            print("=" * 80)
            print(f)
            print("paragraphs:", len(paras))
            for t in paras[:25]:
                print("  |", t[:110])
            # count chars
            total = sum(len(p) for p in paras)
            print("total chars:", total)
        except Exception as exc:
            print(f, "ERROR", exc)


if __name__ == "__main__":
    main()
