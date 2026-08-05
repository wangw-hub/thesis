# -*- coding: utf-8 -*-
import io, re, sys
sys.path.insert(0, r"D:\Research\crypto_thesis\epoch-authorization-r3-prep\scripts\r3_i11")
import m5_transform as m5
t = io.open(m5.SRC, encoding="utf-8").read()
i = t.find("### 参考文献")
j = t.find("### 4．阶段性研究成果", i)
refs = [ln.strip() for ln in t[i:j].splitlines() if re.match(r"^\[\d+\] ", ln.strip())]
print("refs:", len(refs))
years = []
for r in refs:
    m = re.search(r"(19|20)\d{2}", r)
    years.append(int(m.group(0)) if m else 0)
recent21 = sum(1 for y in years if 2021 <= y <= 2026)
recent24 = sum(1 for y in years if 2024 <= y <= 2026)
print("2021-2026:", recent21, f"({recent21/len(refs):.0%})", "| 2024-2026:", recent24)
for r, y in zip(refs, years):
    print(y, "|", r[:70])
