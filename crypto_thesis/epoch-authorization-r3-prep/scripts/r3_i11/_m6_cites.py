# -*- coding: utf-8 -*-
import io, re, sys
sys.path.insert(0, r"D:\Research\crypto_thesis\epoch-authorization-r3-prep\scripts\r3_i11")
import m5_transform as m5
t = io.open(m5.SRC, encoding="utf-8").read()
body = t[:t.find("### 参考文献")]
# find citation groups with context
for m in re.finditer(r"\[(\d+(?:\[\d+)*)\]", body):
    ctx_start = max(0, m.start()-70)
    ctx = body[ctx_start:m.end()+10].replace("\n", " ")
    print(f"{m.group(0):12s} @ {m.start():6d} | ...{ctx[-75:]}")
