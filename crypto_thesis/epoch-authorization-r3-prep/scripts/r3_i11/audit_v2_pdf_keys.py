"""Verify key Chinese strings in the V2 PDF."""
from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(r"D:\Research\crypto_thesis\epoch-authorization-r3-prep")
PDF = ROOT / "docs/final-manuscript/output/THESIS-FORMAT-CANDIDATE-V2.pdf"

KEYS = [
    "表4-2 固定宽度大端编码字段", "表4-3 各阶段复杂度分析",
    "表4-8 不同策略场景下三种表示的适用性", "表5-1 安全目标、机制与证据及结论边界",
    "引理 4.1", "引理 4.4", "定理 4.1", "证毕。■",
    "致\u3000谢", "高建彬", "王\u3000威", "计算机科学与工程学院",
    "电子科技大学", "专业学位硕士学位论文", "摘\u3000要", "目\u3000录",
    "面向非连续时间约束的区块链数据共享", "关键技术研究及实现",
]


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    import pypdfium2 as pdfium

    doc = pdfium.PdfDocument(str(PDF))
    full = "\n".join(doc[i].get_textpage().get_text_range() for i in range(len(doc)))
    for k in KEYS:
        print(f"{k!r}: {full.count(k)}")
    print("---- fuzzy (space-tolerant) ----")
    for k in ["表4-2固定宽度大端编码字段", "表4-3各阶段复杂度分析", "表4-8不同策略场景下三种表示的适用性",
              "表5-1安全目标、机制与证据及结论边界", "致谢", "王威", "摘要", "目录", "证毕",
              "表4-4三种表示的理论与实现特征", "表4-5E2正确性验证汇总", "表4-6E1-C核心边界结果",
              "表4-7二次幂与非二次幂全域补充实验", "表5-2四种方法运行级总体统计", "表5-3四种配对比较"]:
        pat = re.sub(r"([\u4e00-\u9fff])", r"\1 ?", k)
        pat = re.sub(r"([A-Za-z0-9])", r"\1 ?", pat)
        print(f"{k}: {len(re.findall(pat, full))}")
    print("---- TOC pages ----")
    toc = "\n".join(doc[i].get_textpage().get_text_range() for i in (9, 10, 11))
    for k in ["第一章 绪论", "第五章 链上状态驱动的可信授权执行机制", "参考文献", "附录 A 复现说明",
              "攻读硕士学位期间取得的成果", "致\u3000谢", "第六章 版本化密文头部"]:
        pat = re.sub(r"([\u4e00-\u9fff])", r"\1 ?", k)
        pat = re.sub(r"([A-Za-z0-9])", r"\1 ?", pat)
        print(f"TOC {k}: {len(re.findall(pat, toc))}")


if __name__ == "__main__":
    main()
