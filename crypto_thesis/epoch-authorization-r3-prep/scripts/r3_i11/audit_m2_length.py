"""Count Chinese characters per section of the M2 full draft."""
from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(r"D:\Research\crypto_thesis\epoch-authorization-r3-prep")
DRAFT = ROOT / "docs/midterm-report/m2/MIDTERM-REPORT-M2-FULL-DRAFT.md"


def hanzi(s: str) -> int:
    return len(re.findall(r"[\u4e00-\u9fff]", s))


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    text = DRAFT.read_text(encoding="utf-8")
    lines = text.splitlines()
    sections = {}
    cur = "front"
    for ln in lines:
        if ln.startswith("**（") and "）" in ln:
            cur = ln.strip(" *（）")[:12]
        elif ln.startswith("### ") or ln.startswith("## 二"):
            cur = ln.strip("# ")
        sections.setdefault(cur, []).append(ln)
    for k, v in sections.items():
        n = hanzi("\n".join(v))
        print(f"{k}: {n}")
    total = hanzi(text)
    print("TOTAL hanzi:", total)
    # count marker blocks (fig/table/algorithm)
    figs = len(re.findall(r"^\[图：", text, re.M))
    tabs = len(re.findall(r"^\[表：", text, re.M))
    algos = len(re.findall(r"^\[算法：", text, re.M))
    print("figure markers:", figs, "| table markers:", tabs, "| algorithm markers:", algos)
    i = text.find("未按开题计划完成")
    j = text.find("针对上述问题采取何种解决办法")
    if i == -1:
        i = text.find("针对上述问题，后续将围绕")
    if i != -1 and j != -1:
        print("problems section hanzi:", hanzi(text[i:j]))
    if i != -1:
        print("problems section starts at:", i)
    if j != -1:
        print("solutions section starts at:", j)
    for kw in ["这一问题的具体表现包括", "避免读者依据单机数值推断", "用于支撑创新性表述不超过", "避免混淆两类复杂度"]:
        print(f"kw {kw}: {text.count(kw)}")
    a = text.find("## 二、存在的主要问题和解决办法")
    b = text.find("## 三、中期考评审查意见")
    if a != -1 and b != -1:
        sec2 = text[a:b]
        print("section2 hanzi:", hanzi(sec2))
    c = text.find("**（4）研究内容一")
    d = text.find("**（5）研究内容二")
    e = text.find("**（6）研究内容三")
    f = text.find("**（7）三项研究内容")
    if c != -1 and d != -1:
        print("RC1 hanzi:", hanzi(text[c:d]))
    if d != -1 and e != -1:
        print("RC2 hanzi:", hanzi(text[d:e]))
    if e != -1 and f != -1:
        print("RC3 hanzi:", hanzi(text[e:f]))
    g = text.find("**（1）研究背景")
    h = text.find("**（4）研究内容一")
    if g != -1 and h != -1:
        print("background+target+route hanzi:", hanzi(text[g:h]))


if __name__ == "__main__":
    main()
