"""Scan the assembled DOCX for leftover internal/stage markers."""
from __future__ import annotations

import re
import sys
from pathlib import Path

from docx import Document


ROOT = Path(r"D:\Research\crypto_thesis\epoch-authorization-r3-prep")
DOCX = ROOT / "docs/final-manuscript/output/THESIS-FORMAT-CANDIDATE-V1.docx"

PATTERNS = [
    r"\bI(?:9|10|11|12|13|14|15)\b", r"PILOT", r"FORMAL_", r"LITERATURE_VERIFICATION",
    r"\[文献", r"docs/", r"experiments/", r"scripts/", r"来源：", r"待核验", r"待补充",
    r"F9", r"更新域", r"内部注记", r"R3Formal", r"prepr", r"candidate", r"CANDIDATE",
]


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    doc = Document(str(DOCX))
    text = "\n".join(p.text for p in doc.paragraphs)
    # exclude reference section URLs from the docs/ path scan
    head = text.split("参考文献", 1)[0]
    for pat in PATTERNS:
        hits = sorted(set(re.findall(pat, head)))
        if hits:
            print(f"{pat}: {len(hits)} -> {hits[:12]}")
            for m in list(re.finditer(pat, head))[:6]:
                ctx = head[max(0, m.start() - 40):m.end() + 40].replace("\n", " ")
                print("    ...", ctx)
    print("scan done")


if __name__ == "__main__":
    main()
