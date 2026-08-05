"""Dump reflowed body paragraphs per chapter for reconstruction decisions."""
from __future__ import annotations

import io
import re
import sys
from pathlib import Path

from analyze_reflow import reflow, classify


ROOT = Path(r"D:\Research\crypto_thesis\epoch-authorization-r3-prep")
MASTER = ROOT / "docs/final-manuscript/MASTER-SOURCE.md"

CHAPTERS = {
    "ch1": "第一章 绪论",
    "ch2": "第二章 相关工作与技术基础",
    "ch3": "第三章 总体技术路线与三项研究内容接口",
    "ch4": "第四章 非连续时间策略规范化编译方法",
    "ch5": "第5章 链上状态驱动的可信授权执行机制",
    "ch6": "第六章 版本化密文头部与前瞻性撤销闭环机制",
    "ch7": "第七章 总结与展望",
}


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    which = sys.argv[1] if len(sys.argv) > 1 else "ch1,ch2,ch3,ch7"
    text = io.open(MASTER, encoding="utf-8").read()
    paras = reflow(text)
    chapter = "front"
    bucket: dict[str, list[tuple[int, str, str]]] = {}
    for idx, (kind, raw) in enumerate(paras):
        c = classify(raw)
        m = re.match(r"^(#{1,4})\s*(.*)$", raw.strip())
        if c == "heading" and m:
            title = m.group(2).strip()
            if re.match(r"^(第[一二三四五六七1-7]章|参考文献|附录)", title):
                chapter = title
        bucket.setdefault(chapter, []).append((idx, c, raw))
    for key in which.split(","):
        ch = CHAPTERS.get(key)
        if not ch:
            continue
        print(f"\n========== {ch} ==========")
        for idx, c, raw in bucket.get(ch, []):
            if c != "body":
                continue
            s = re.sub(r"\s+", " ", raw).strip()
            print(f"[{idx}] {s}")


if __name__ == "__main__":
    main()
