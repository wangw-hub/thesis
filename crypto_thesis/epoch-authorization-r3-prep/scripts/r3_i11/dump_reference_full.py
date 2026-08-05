"""Extract full reference report content (all table cells, full text)."""
from __future__ import annotations

import sys
from pathlib import Path

from docx import Document


REFERENCE = Path(r"D:\Users\wangw\Desktop\中期和小论文\shy-专业学位研究生学位论文中期考评表.docx")


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    doc = Document(str(REFERENCE))
    for ti, t in enumerate(doc.tables):
        print(f"\n========== TABLE {ti} ==========")
        for ri, row in enumerate(t.rows):
            seen = set()
            texts = []
            for c in row.cells:
                if id(c._tc) in seen:
                    continue
                seen.add(id(c._tc))
                texts.append(c.text)
            for ci, txt in enumerate(texts):
                print(f"--- r{ri}c{ci} (len={len(txt)}) ---")
                print(txt[:2500])


if __name__ == "__main__":
    main()
