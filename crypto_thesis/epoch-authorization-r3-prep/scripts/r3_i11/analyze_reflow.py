"""Analyze paragraph fragmentation after markdown line-reflow."""
from __future__ import annotations

import io
import re
import sys
from pathlib import Path


ROOT = Path(r"D:\Research\crypto_thesis\epoch-authorization-r3-prep")
MASTER = ROOT / "docs/final-manuscript/MASTER-SOURCE.md"


def reflow(text: str) -> list[tuple[str, str]]:
    """Group consecutive non-blank lines into paragraphs (single newline -> join)."""
    paras: list[tuple[str, str]] = []
    cur: list[str] = []
    in_fence = False
    fence = []
    fence_lang = ""

    def flush():
        if cur:
            paras.append(("para", "\n".join(cur)))
            cur.clear()

    for ln in text.splitlines():
        s = ln.strip()
        if in_fence:
            fence.append(ln)
            if s.startswith("```"):
                paras.append(("code", "\n".join(fence)))
                fence, in_fence = [], False
            continue
        if s.startswith("```"):
            flush()
            in_fence = True
            fence_lang = s[3:]
            fence = [ln]
            continue
        if re.match(r"^(#{1,4})\s", s) or s.startswith("![") or s.startswith("|") or s.startswith("\\[") \
                or re.match(r"^\*\*(图|表|算法)", s):
            flush()
            paras.append(("marker", ln))
            continue
        if not s:
            flush()
            continue
        cur.append(ln)
    flush()
    if fence:
        paras.append(("code", "\n".join(fence)))
    return paras


def classify(p: str) -> str:
    s = p.strip()
    if re.match(r"^(#{1,4})\s", s):
        return "heading"
    if s.startswith("|"):
        return "table"
    if s.startswith("!["):
        return "image"
    if s.startswith("\\["):
        return "equation"
    if re.match(r"^\*\*(图|表|算法)", s):
        return "caption"
    if re.match(r"^\[\d+\]\s", s):
        return "reference"
    if s.startswith(">"):
        return "quote"
    return "body"


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    text = io.open(MASTER, encoding="utf-8").read()
    paras = reflow(text)
    print("total blocks:", len(paras))
    chapter = "front"
    seen_chapters = []
    stats = {}
    by_chapter: dict[str, list[tuple[str, str, str]]] = {}
    for kind, raw in paras:
        c = classify(raw)
        m = re.match(r"^(#{1,4})\s*(.*)$", raw.strip())
        if c == "heading" and m:
            title = m.group(2).strip()
            if re.match(r"^(第[一二三四五六七1-7]章|参考文献|附录)", title):
                chapter = title
                seen_chapters.append(title)
        key = f"{chapter}::{c}"
        by_chapter.setdefault(chapter, []).append((kind, c, raw))
        stats[key] = stats.get(key, 0) + 1
    print("detected chapters:", seen_chapters)
    if "第四章" not in " ".join(seen_chapters):
        for kind, raw in paras:
            s = raw.strip()
            if s.startswith("#") and ("四" in s[:20]):
                print("DEBUG heading line:", repr(raw[:40]))
    for k in sorted(stats):
        print(k, stats[k])
    print()
    for ch in ["第一章 绪论", "第二章 相关工作与技术基础", "第三章 总体技术路线与三项研究内容接口",
               "第四章 非连续时间策略规范化编译方法", "第5章 链上状态驱动的可信授权执行机制",
               "第六章 版本化密文头部与前瞻性撤销闭环机制", "第七章 总结与展望"]:
        items = by_chapter.get(ch, [])
        bodies = [(i, raw) for i, (k, c, raw) in enumerate(items) if c == "body"]
        short = [raw for (_i, raw) in bodies if 0 < len(re.sub(r"\s", "", raw)) < 100]
        print(f"== {ch}: body blocks={len(bodies)} short(<100c)={len(short)}")
        for raw in short:
            s = re.sub(r"\s+", " ", raw).strip()
            print("   SHORT:", s[:120])


if __name__ == "__main__":
    main()
