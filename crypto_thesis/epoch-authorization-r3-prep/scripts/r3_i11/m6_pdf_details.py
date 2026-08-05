# -*- coding: utf-8 -*-
"""M6: detailed PDF text checks (equations, algorithms, refs, captions)."""
from __future__ import annotations

import re
import sys
from pathlib import Path

import fitz


ROOT = Path(r"D:\Research\crypto_thesis\epoch-authorization-r3-prep")
PDF = ROOT / "docs/midterm-report/m6/output/王威-专业学位研究生学位论文中期考评表-M6候选稿.pdf"


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    doc = fitz.open(str(PDF))
    text = "\n".join(p.get_text() for p in doc)

    print("=== equation numbers found in order ===")
    nums = [int(m.group(1)) for m in re.finditer(r"\((\d{1,2})\)", text)]
    eq_nums = [n for n in nums if 1 <= n <= 17]
    print(eq_nums)
    print("sequential 1..17:", eq_nums == list(range(1, 18)))

    print("\n=== algorithm titles ===")
    for i in range(1, 9):
        pat = f"算法{i}"
        idx = text.find(pat)
        ctx = text[idx:idx + 60].replace("\n", " ") if idx >= 0 else "NOT FOUND"
        print(f"算法{i}: {ctx}")

    print("\n=== 式（n） references ===")
    print(re.findall(r"式（(\d+)）", text))

    print("\n=== figure captions ===")
    for m in re.finditer(r"图(\d+) ([^\n]{0,60})", text):
        cap = m.group(2).strip()
        if cap:
            print(m.group(1), "|", cap[:60])

    print("\n=== reference entries 1..31 ===")
    refs = re.findall(r"^\[(\d{1,2})\]\s*(.+)", text, re.M)
    seen = []
    for n, rest in refs:
        nn = int(n)
        if 1 <= nn <= 31 and nn not in seen:
            seen.append(nn)
    print("first-seen ref numbers:", seen)
    print("sequential:", seen == list(range(1, 32)))

    print("\n=== math glyph sanity (S(P), I*, C(P), pd) ===")
    for pat in ["S(P)", "I*", "C(P)", "SHA-256", "HPKE", "AES-256-GCM"]:
        print(pat, "->", text.count(pat))


if __name__ == "__main__":
    main()
