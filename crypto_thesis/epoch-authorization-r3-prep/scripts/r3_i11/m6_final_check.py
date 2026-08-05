# -*- coding: utf-8 -*-
"""M6: final consolidated checks on source + PDF."""
from __future__ import annotations

import io
import re
import sys
from pathlib import Path

import fitz


ROOT = Path(r"D:\Research\crypto_thesis\epoch-authorization-r3-prep")
M6 = ROOT / "docs/midterm-report/m6/M6-MIDTERM-SOURCE.md"
PDF = ROOT / "docs/midterm-report/m6/output/王威-专业学位研究生学位论文中期考评表-M6候选稿.pdf"


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    t = io.open(M6, encoding="utf-8").read()
    doc = fitz.open(str(PDF))
    pdf_text = "\n".join(p.get_text() for p in doc)

    print("=== 式（7）式（8）refs ===")
    for m in re.finditer(r"式（(\d+)）", t):
        print(m.group(1), end=" ")
    print()

    print("=== capability signature lead-in present ===")
    print("签名关系如式（7）、式（8）所示" in t)

    print("=== 阶段性实验结果与研究认识总结 absent ===")
    print("阶段性实验结果与研究认识总结" not in t)

    print("=== problems count ===")
    seg = t[t.find("## 二、存在的主要问题和解决办法"):]
    print("问题一/问题二/问题三:", seg.count("问题一"), seg.count("问题二"), seg.count("问题三"))
    # count （1）（2）（3） problem/solution items
    print("（1）（2）（3） items in problems section:", len(re.findall(r"（[123]）", seg)))

    print("=== stage results (1 paper + 2 patents) ===")
    s = t[t.find("### 4．阶段性研究成果"):t.find("## 二、存在的主要问题和解决办法")]
    print("论文行:", "论文" in s, "| 专利1:", "一种非连续时间访问策略的确定性编译方法" in s,
          "| 专利2:", "一种链上可信授权与版本化密文对象管理方法" in s)

    print("=== final tags in PDF text ===")
    for tag in ["RC1", "RC2", "RC3", "E1-A", "CAP2", "HEADER_ONLY", "BODY_ROTATION", "V13", "Pilot"]:
        n = pdf_text.count(tag)
        if n:
            print(tag, n)
    print("done")


if __name__ == "__main__":
    main()
