# -*- coding: utf-8 -*-
import io, re, sys
sys.path.insert(0, r"D:\Research\crypto_thesis\epoch-authorization-r3-prep\scripts\r3_i11")
import m5_transform as m5
t = io.open(m5.SRC, encoding="utf-8").read()
print("=== internal tags in M5 source ===")
tags = ["RC1","RC2","RC3","E1-A","E1-B","E1-C","V13","v13","P9","Pilot","Formal","attempt","runId","SHA","I9","I10","I11","I12","I13","I14","I15","I16","I17","CAP2","Baseline-I","Proposed-C","HEADER_ONLY","BODY_ROTATION","E2","E3","E4","E5"]
for tag in tags:
    n = t.count(tag)
    if n:
        print(f"{tag}: {n}")
print("=== equations ===")
eqs = [m.group(1) for m in re.finditer(r"\[公式：([^\]]+)\]", t)]
print("display equations:", len(eqs))
for i, e in enumerate(eqs, 1):
    print(i, "|", e[:80])
